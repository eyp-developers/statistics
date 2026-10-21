import { loginAs } from '../../support/e2e-api/login';
import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

test.describe('active debate and round', () => {
  test('setting the active debate announces it on the session page', async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    // The session page only announces the active debate when the session had activity today.
    await addSessionData(session.id, { points: [{ committee: 'AFCO' }] });
    await loginAs(page, session.id, 'admin');
    await page.goto(`/manage/${session.id}/`);

    await page.getByLabel('Set Active Debate:').selectOption('AFCO');
    await page.getByRole('button', { name: 'Update Active Debate' }).click();

    await expect(page.getByText('Active Debate Saved')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Active Debate: AFCO' })).toBeVisible();

    await page.goto(`/session/${session.id}/`);
    await expect(page.getByRole('heading', { name: 'AFCO is being debated right now!' })).toBeVisible();
  });

  test('setting the active round makes it the default in the submission forms', async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    const afco = session.committees.find((c) => c.name === 'AFCO')!;
    await loginAs(page, session.id, 'admin');
    await page.goto(`/manage/${session.id}/`);

    await page.getByLabel('Set Active Round:').selectOption('2');
    await page.getByRole('button', { name: 'Update Active Round' }).click();

    await expect(page.getByText('Active Round Saved')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Active Round: 2' })).toBeVisible();

    await page.goto(`/session/${session.id}/joint/${afco.id}/`);
    await expect(page.getByLabel('Round Number:')).toHaveValue('2');
    await page.goto(`/session/${session.id}/joint/all/`);
    await expect(page.getByLabel('Round Number:')).toHaveValue('2');
  });
});
