import type { Page } from '@playwright/test';
import { closeDatePickers } from '../../support/datepicker';
import { loginAs } from '../../support/e2e-api/login';
import { uniqueSessionName, type CreatedSession } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

async function openEditPage(page: Page, session: CreatedSession) {
  await loginAs(page, session.id, 'admin');
  await page.goto(`/edit/${session.id}/`);
  await expect(page).toHaveTitle(`Edit - ${session.name} | GA Statistics`);
}

async function save(page: Page) {
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByText('Session Updated')).toBeVisible();
}

test.describe('editing a session', () => {
  test('making a session visible puts it on the home page', async ({ page, createSession }) => {
    // The home page lists sessions newest first, 12 per page. A start date far in the future keeps this one
    // on page 1 while other tests create sessions in parallel.
    const session = await createSession({ start_date: '2099-11-01', end_date: '2099-11-10' });
    const sessionCard = page.getByRole('heading', { name: session.name, exact: true });

    await page.goto('/');
    await expect(sessionCard).toBeHidden();

    await openEditPage(page, session);
    // The styled toggle hides the real checkbox, so click its label like a user would.
    const visible = page.getByRole('checkbox', { name: 'Is visible', exact: true });
    await expect(visible).not.toBeChecked();
    await page.getByText('Is visible', { exact: true }).click();
    await expect(visible).toBeChecked();
    await save(page);

    await page.goto('/');
    await expect(sessionCard).toBeVisible();
  });

  test('saves changed details', async ({ page, createSession }) => {
    const session = await createSession({ max_rounds: 3 });
    const newName = uniqueSessionName();
    await openEditPage(page, session);

    await page.getByLabel('Name', { exact: true }).fill(newName);
    await page.getByLabel('Description', { exact: true }).fill('Renamed by an end-to-end test');
    await page.getByLabel('Start date', { exact: true }).fill('2027-03-01');
    await page.getByLabel('End date', { exact: true }).fill('2027-03-05');
    await closeDatePickers(page);
    await page.getByLabel('Max rounds', { exact: true }).fill('5');
    await save(page);

    await page.reload();
    await expect(page).toHaveTitle(`Edit - ${newName} | GA Statistics`);
    await expect(page.getByLabel('Name', { exact: true })).toHaveValue(newName);
    await expect(page.getByLabel('Description', { exact: true })).toHaveValue('Renamed by an end-to-end test');
    await expect(page.getByLabel('Start date', { exact: true })).toHaveValue('2027-03-01');
    await expect(page.getByLabel('End date', { exact: true })).toHaveValue('2027-03-05');
    await expect(page.getByLabel('Max rounds', { exact: true })).toHaveValue('5');
  });

  test('keeps the statistics mode when saving without changing it', async ({ page, createSession }) => {
    // Known bug 4: the edit view pre-fills the key 'statisticscore' instead of 'statistics'
    // (statisticscore/views/protected/edit.py), so the dropdown always shows "Statistics Only" and saving
    // quietly switches the session to that mode.
    test.fail();

    const session = await createSession({ mode: 'C' });
    await openEditPage(page, session);
    // Matched by its start: with the bug, the label also carries a "This field is required." error.
    const mode = page.getByLabel(/^Statistics\b/);
    await expect(mode).toHaveValue('C');

    await save(page);
    await page.reload();
    await expect(mode).toHaveValue('C');
  });

  test('saving without a new picture keeps the existing one', async ({ page, createSession }) => {
    const session = await createSession();
    await openEditPage(page, session);

    await page.getByLabel('Description', { exact: true }).fill('Changed without a new picture');
    await save(page);

    // The session page draws its header from the picture and fails to render without one.
    const response = await page.goto(`/session/${session.id}/`);
    expect(response?.status()).toBe(200);
    await expect(page.getByRole('heading', { name: session.name, exact: true })).toBeVisible();
    await expect(page.getByText('Changed without a new picture')).toBeVisible();
  });
});
