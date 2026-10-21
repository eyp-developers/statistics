import { loginAs } from '../../support/e2e-api/login';
import { expect, test } from '../../support/fixtures';

test.describe('managing committees', () => {
  test('adds a committee with subtopics, including an automatic "General"', async ({ page, createSession }) => {
    const session = await createSession();
    await loginAs(page, session.id, 'admin');
    await page.goto(`/committees/${session.id}/`);

    await page.getByLabel('Committee Name:').fill('ENVI');
    await page.getByLabel('Committee Topic:').fill('How should the EU cut emissions?');
    await page.getByRole('textbox', { name: 'Subtopic', exact: true }).fill('Emissions');
    await page.getByRole('link', { name: 'Add Subtopic' }).click();
    await page.getByRole('textbox', { name: 'Subtopic', exact: true }).last().fill('Energy');
    await page.getByRole('button', { name: 'Save Committee' }).click();

    await expect(page.getByText('Committee Saved')).toBeVisible();
    const row = page.getByRole('row').filter({ hasText: 'ENVI' });
    await expect(row).toContainText('How should the EU cut emissions?');
    await expect(row).toContainText('General, Emissions, Energy');

    await page.reload();
    await expect(row).toContainText('General, Emissions, Energy');
  });

  test('renames a committee and changes its subtopics', async ({ page, createSession }) => {
    const session = await createSession({
      committees: [{ name: 'ENVI', topic: 'Climate', subtopics: ['Emissions', 'Energy'] }],
    });
    await loginAs(page, session.id, 'admin');
    await page.goto(`/committees/${session.id}/`);

    await page.getByRole('link', { name: 'Edit ENVI' }).click();
    // The form is filled in from the committees API, so wait for it before changing anything.
    await expect(page.getByLabel('Committee Name:')).toHaveValue('ENVI');
    const subtopics = page.getByRole('textbox', { name: 'Subtopic', exact: true });
    await expect(subtopics).toHaveCount(2);

    await page.getByLabel('Committee Name:').fill('CLIM');
    await subtopics.first().fill('Oceans');
    await page.getByRole('button', { name: 'Delete subtopic' }).last().click();
    await page.getByRole('button', { name: 'Save Committee' }).click();

    await expect(page.getByText('Committee Saved')).toBeVisible();
    await page.reload();
    await expect(page.getByRole('row').filter({ hasText: 'ENVI' })).toHaveCount(0);
    const row = page.getByRole('row').filter({ hasText: 'CLIM' });
    await expect(row).toContainText('General, Oceans');
    await expect(row).not.toContainText('Energy');

    await page.goto(`/session/${session.id}/`);
    await expect(page.getByRole('link', { name: 'CLIM', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: 'ENVI', exact: true })).toHaveCount(0);
  });

  test('deletes a committee after confirming', async ({ page, createSession }) => {
    const session = await createSession({ committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    await loginAs(page, session.id, 'admin');
    await page.goto(`/committees/${session.id}/`);

    page.once('dialog', (dialog) => dialog.accept());
    await page.getByRole('link', { name: 'Delete ENVI' }).click();
    await expect(page.getByRole('row').filter({ hasText: 'ENVI' })).toHaveCount(0);

    await page.reload();
    await expect(page.getByRole('row').filter({ hasText: 'ENVI' })).toHaveCount(0);
    await expect(page.getByRole('row').filter({ hasText: 'AFCO' })).toBeVisible();
  });

  test('rejects a committee name longer than 8 characters', async ({ page, createSession }) => {
    const session = await createSession();
    await loginAs(page, session.id, 'admin');
    await page.goto(`/committees/${session.id}/`);

    await page.getByLabel('Committee Name:').fill('TOOLONGNAME');
    await page.getByLabel('Committee Topic:').fill('A topic');
    await page.getByRole('button', { name: 'Save Committee' }).click();

    await expect(page.getByText(/at most 8 characters/)).toBeVisible();
    await page.reload();
    await expect(page.getByRole('row').filter({ hasText: 'TOOLONGNAME' })).toHaveCount(0);
  });
});

test.describe('committee permissions', () => {
  test("another session's admin cannot delete a committee", async ({ page, createSession }) => {
    const session = await createSession({ committees: [{ name: 'ENVI' }] });
    const otherSession = await createSession();
    await loginAs(page, otherSession.id, 'admin');
    // The other session's committees page can't be opened, so post the delete the way that page's script does,
    // with the CSRF token the admin's own committees page hands out.
    await page.goto(`/committees/${otherSession.id}/`);
    const csrfToken = (await page.context().cookies()).find((cookie) => cookie.name === 'csrftoken')?.value ?? '';

    const response = await page.request.post(`/committees/${session.id}/`, {
      headers: { 'X-CSRFToken': csrfToken },
      form: { delete: 'true', pk: session.committees[0].id },
    });
    expect(response.status()).toBe(403);

    await loginAs(page, session.id, 'admin');
    await page.goto(`/committees/${session.id}/`);
    await expect(page.getByRole('row').filter({ hasText: 'ENVI' })).toBeVisible();
  });
});
