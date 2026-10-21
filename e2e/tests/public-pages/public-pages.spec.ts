import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

test.describe('public pages', () => {
  test('get started page explains what GA Statistics can do', async ({ page }) => {
    await page.goto('/get_started/');
    await expect(page.getByRole('heading', { name: 'Welcome to GA Statistics!' })).toBeVisible();

    // The sections are collapsed until their heading is clicked.
    const runningOrder = page.getByRole('heading', { name: 'Running Order Statistics (with or without point content)' });
    await expect(runningOrder).toBeHidden();
    await page.getByRole('link', { name: 'What can I do with GA Statistics?' }).click();
    await expect(runningOrder).toBeVisible();
  });

  test('changelog renders the changelog', async ({ page }) => {
    await page.goto('/changelog/');
    await expect(page.getByRole('heading', { name: 'Changelog', level: 1 })).toBeVisible();
    // CHANGELOG.md is rendered from markdown: one dated heading per release.
    await expect(page.getByRole('heading', { level: 3, name: /^\d{4}-\d{2}-\d{2}$/ }).first()).toBeVisible();
  });

  test('high scores rank sessions by total votes and leave out hidden ones', async ({ page, createSession }) => {
    const committees = [{ name: 'ENVI' }, { name: 'AFCO' }];
    const busy = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    const hidden = await createSession({ visible: false, committees, active_debate: 'ENVI' });
    // Far more votes than any other test creates, so the visible session makes the top 5.
    for (const session of [busy, hidden]) {
      await addSessionData(session.id, {
        points: [{ committee: 'AFCO' }],
        votes: [{ committee: 'AFCO', in_favour: 20000, against: 12000 }],
      });
    }

    await page.goto('/highscores/');
    const mostVotes = page.getByRole('table').filter({ has: page.getByRole('columnheader', { name: 'Total Votes' }) });
    await expect(mostVotes.getByRole('row', { name: busy.name })).toContainText('32000');
    await expect(page.getByText(hidden.name)).toHaveCount(0);

    const rankedRows = await mostVotes.getByRole('row').filter({ has: page.getByRole('cell') }).all();
    const totals = await Promise.all(rankedRows.map(async (row) => Number(await row.getByRole('cell').last().textContent())));
    expect(totals, 'ranked by total votes, highest first').toEqual([...totals].sort((a, b) => b - a));
  });

  test('topics page lists the topics of committees and filters them by text', async ({ page, createSession }) => {
    const topic = `Topic ${crypto.randomUUID()}: how should the EU regulate drones?`;
    const session = await createSession({ visible: true, committees: [{ name: 'TRAN', topic }] });

    await page.goto('/topics/');
    await expect(page.getByRole('heading', { name: 'Topics' })).toBeVisible();

    await page.getByLabel('Topic Text, Area or Type').fill(topic.slice(0, 42));
    await page.getByRole('button', { name: 'filter' }).click();

    const row = page.getByRole('row', { name: new RegExp(topic.slice(0, 42)) });
    await expect(row).toHaveCount(1);
    await expect(row.getByRole('cell', { name: 'TRAN', exact: true })).toBeVisible();
    // The "used at" links are marked up with role="button" (statisticscore/tables.py).
    await expect(row.getByRole('button', { name: session.name })).toHaveAttribute(
      'href',
      `/session/${session.id}/debate/${session.committees[0].id}/`,
    );
  });

  test('topics page filters by committee name', async ({ page, createSession }) => {
    // Bug: the committee filter's raw SQL uses the old statistics_* table names and ILIKE (statisticscore/filters.py),
    // so filtering by committee crashes with a 500.
    test.fail();
    const topic = `Topic ${crypto.randomUUID()}`;
    await createSession({ committees: [{ name: 'SEDE', topic }] });

    await page.goto('/topics/');
    await page.getByLabel('Committee name').fill('SEDE');
    await page.getByRole('button', { name: 'filter' }).click();
    await expect(page.getByRole('row', { name: new RegExp(topic) })).toBeVisible();
  });

  test('unknown pages answer 404 with a not-found page', async ({ page }) => {
    const response = await page.goto(`/no-such-page-${crypto.randomUUID()}/`);
    // Locally the e2e server runs with DEBUG on, so Django's own 404 page is shown with status 404. On a target with
    // DEBUG off the custom 404 page is shown instead, with status 200 (known bug 8), and this assertion fails there.
    expect(response?.status()).toBe(404);
    await expect(page.getByText(/page not found/i).first()).toBeVisible();
  });
});
