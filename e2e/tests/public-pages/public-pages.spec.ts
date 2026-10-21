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

  test('high scores page loads', async ({ page }) => {
    const response = await page.goto('/highscores/');
    expect(response?.status()).toBe(200);
    await expect(page).toHaveTitle(/GA Statistics/);
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
    // Locally the e2e server runs with DEBUG on, so Django's own 404 page is shown. With DEBUG off it's the custom one.
    expect(response?.status()).toBe(404);
    await expect(page.getByText(/page not found/i).first()).toBeVisible();
  });

  // No session will ever get this ID in the e2e database.
  const unknownId = 2_147_483_000;

  test('an unknown session answers 404', async ({ page }) => {
    const response = await page.goto(`/session/${unknownId}/`);
    expect(response?.status()).toBe(404);
    await expect(page.getByText(/page not found/i).first()).toBeVisible();
  });

  test('the debate page of an unknown session or committee answers 404', async ({ page, createSession }) => {
    const session = await createSession({ committees: [{ name: 'ENVI' }] });

    const unknownSession = await page.goto(`/session/${unknownId}/debate/${session.committees[0].id}/`);
    expect(unknownSession?.status()).toBe(404);
    await expect(page.getByText(/page not found/i).first()).toBeVisible();

    const unknownCommittee = await page.goto(`/session/${session.id}/debate/${unknownId}/`);
    expect(unknownCommittee?.status()).toBe(404);
    await expect(page.getByText(/page not found/i).first()).toBeVisible();
  });
});
