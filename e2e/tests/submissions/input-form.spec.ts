import { expect, test } from '../../support/fixtures';
import { committeeId, debateSetup, openAsChair } from './submission-session';

test("the input form records a committee's next subtopics", async ({ page, createSession }) => {
  const session = await createSession({ ...debateSetup, mode: 'R' });

  await openAsChair(page, session, `input/${committeeId(session, 'AFCO')}/`);
  await expect(page.getByRole('heading', { name: "What's AFCO's next point on ENVI about?" })).toBeVisible();
  await expect(page.getByText('Next Point will be on: None')).toBeVisible();

  await page.getByLabel('Next Subtopics').selectOption(['Emissions', 'Energy']);
  await page.getByRole('button', { name: 'Submit' }).click();

  await expect(page.getByText('Your Point was successfully sent to the board')).toBeVisible();
  await expect(page.getByText('Next Point will be on: Emissions Energy')).toBeVisible();
});
