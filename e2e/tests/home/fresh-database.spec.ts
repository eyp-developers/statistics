import { addSessionData, uniqueSessionName } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

// These tests look at the whole site, so they empty the database first. They run in the fresh-db project, one at a
// time, after everything else, and are skipped on targets that don't allow a reset.

test.describe('home page on a fresh install', () => {
  test('offers to create the first session when there are none', { tag: '@fresh-db' }, async ({
    page,
    freshDatabase,
  }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'No sessions are available. How do I create a session?' })).toBeVisible();

    await page.getByRole('link', { name: 'Create your first session' }).click();
    await expect(page).toHaveURL(/\/create_session\/$/);
  });

  test('shows 12 sessions per page, newest first', { tag: '@fresh-db' }, async ({
    page,
    freshDatabase,
    createSession,
  }) => {
    // Session i starts on day i of January, so the last one created is the newest.
    const names: string[] = [];
    for (let day = 1; day <= 13; day++) {
      const session = await createSession({
        name: uniqueSessionName('Paged'),
        visible: true,
        start_date: `2030-01-${String(day).padStart(2, '0')}`,
        end_date: '2030-01-31',
      });
      names.push(session.name);
    }
    const sessionCards = page.getByRole('heading', { level: 1, name: /^Paged / });

    await page.goto('/');
    await expect(sessionCards).toHaveCount(12);
    await expect(sessionCards.first()).toHaveText(names[12]);
    await expect(page.getByRole('heading', { name: names[0], exact: true })).toHaveCount(0);

    await page.getByRole('link', { name: 'Older events' }).click();
    await expect(sessionCards).toHaveCount(1);
    await expect(sessionCards).toHaveText(names[0]);

    await page.getByRole('link', { name: 'More recent events' }).click();
    await expect(sessionCards).toHaveCount(12);
  });
});

test.describe('high scores on a fresh install', () => {
  test('ranks visible sessions by total votes', { tag: '@fresh-db' }, async ({ page, freshDatabase, createSession }) => {
    const committees = [{ name: 'ENVI' }, { name: 'AFCO' }];
    const busy = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    const quiet = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    const hidden = await createSession({ visible: false, committees, active_debate: 'ENVI' });
    for (const [session, votes] of [[busy, 40], [quiet, 10], [hidden, 99]] as const) {
      await addSessionData(session.id, {
        points: [{ committee: 'AFCO' }],
        votes: [{ committee: 'AFCO', in_favour: votes / 2, against: votes / 2 }],
      });
    }

    await page.goto('/highscores/');
    const mostVotes = page.getByRole('table').filter({ has: page.getByRole('columnheader', { name: 'Total Votes' }) });
    await expect(mostVotes.getByRole('row')).toHaveText(['# Session Total Votes', `1 ${busy.name} 40`, `2 ${quiet.name} 10`]);
    // Hidden sessions never appear in the rankings.
    await expect(page.getByText(hidden.name)).toHaveCount(0);
  });
});
