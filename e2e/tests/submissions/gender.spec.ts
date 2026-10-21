import { expect, test } from '../../support/fixtures';
import { debateSetup, liveUpdate, openAsChair } from './submission-session';

test('with gender tracking on, a submitted gender entry shows in the table', async ({ page, createSession }) => {
  const session = await createSession({ ...debateSetup, mode: 'JF', gender_enabled: true });

  await openAsChair(page, session, '');
  await page.goto(`/gender/${session.id}/`);
  await expect(page.getByRole('heading', { name: `Track Gender: ${session.name}` })).toBeVisible();

  // The proposing committee defaults to the debate going on.
  await expect(page.getByLabel('Proposing Committee')).toHaveValue(String(session.committees[0].id));
  await page.getByLabel('Proposing Committee').selectOption('AFCO');
  await page.getByLabel('Gender:', { exact: true }).selectOption('Female');
  await page.getByRole('button', { name: 'Submit' }).click();
  await expect(page.getByText('Gender Successfully Submitted')).toBeVisible();

  const row = page.getByRole('row').filter({ has: page.getByRole('cell', { name: 'AFCO', exact: true }) });
  await expect(row).toBeVisible(liveUpdate);
  await expect(row.getByRole('cell', { name: 'F', exact: true })).toBeVisible();
});
