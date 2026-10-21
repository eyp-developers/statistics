import type { Page } from '@playwright/test';
import { setSessionState } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';
import { committeeId, debateSetup, liveUpdate, openAsChair, openDebatePage } from './submission-session';

async function fillVotes(page: Page, votes: { inFavour: number; against: number; abstentions: number; absent: number }) {
  await page.getByLabel('Votes In Favour').fill(String(votes.inFavour));
  await page.getByLabel('Votes Against').fill(String(votes.against));
  await page.getByLabel('Abstentions').fill(String(votes.abstentions));
  await page.getByLabel('Absent').fill(String(votes.absent));
}

test.describe('voting', () => {
  test("a committee's votes are counted on the debate page", async ({ page, createSession }) => {
    const session = await createSession({ ...debateSetup, mode: 'JF' });

    await openAsChair(page, session, `vote/${committeeId(session, 'AFCO')}/`);
    await fillVotes(page, { inFavour: 10, against: 3, abstentions: 1, absent: 2 });
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText("Your Committee's Votes were successfully submitted")).toBeVisible();

    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'Votes Counted: 16' })).toBeVisible(liveUpdate);
    await expect(page.getByRole('heading', { name: 'Committees Counted: 1/3' })).toBeVisible(liveUpdate);
    await expect(page.getByRole('heading', { name: 'In Favour: 10' })).toBeVisible(liveUpdate);
    await expect(page.getByRole('heading', { name: 'Against: 3' })).toBeVisible(liveUpdate);
  });

  test('the all-committees vote form saves and returns to the form', async ({ page, createSession }) => {
    // Bug 3: the view redirects to the per-committee URL with no committee (views/protected/vote.py:53), so the
    // vote is saved but the chair gets a 500 and is likely to submit again, counting the votes twice.
    test.fail();
    const session = await createSession({ ...debateSetup, mode: 'JF' });

    await openAsChair(page, session, 'vote/all/');
    await page.getByLabel('Committee').selectOption('ITRE');
    await fillVotes(page, { inFavour: 8, against: 5, abstentions: 2, absent: 1 });
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText("Your Committee's Votes were successfully submitted")).toBeVisible();
  });

  test('with voting turned off, the voting sections are not shown', async ({ page, createSession }) => {
    const session = await createSession({ ...debateSetup, mode: 'JF' });

    // Control: with voting on, both pages show the voting summary.
    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'Voting Summary' })).toBeVisible();

    await setSessionState(session.id, { voting_enabled: false });

    await page.goto(`/session/${session.id}/`);
    await expect(page.getByRole('heading', { name: 'Debates' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Voting Summary' })).toBeHidden();

    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'ENVI', level: 1 })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Voting Summary' })).toBeHidden();
  });
});
