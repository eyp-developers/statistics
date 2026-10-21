import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';
import { findSessionCard, sessionCards } from '../../support/home-page';

// The home page lists visible sessions newest first, 12 per page, and other tests create sessions at the same
// time, so these tests never assume which page a session lands on unless they make it the newest.

test.describe('home page', () => {
  test("links each visible session's card to its session page", async ({ page, createSession }) => {
    const session = await createSession({ visible: true });

    const card = await findSessionCard(page, session.name);
    expect(card, 'the session is listed on the home page').not.toBeNull();
    await card!.click();

    await expect(page).toHaveURL(new RegExp(`/session/${session.id}/$`));
    await expect(page.getByRole('heading', { name: session.name, level: 1 })).toBeVisible();
  });

  test('flags sessions with activity today', async ({ page, createSession }) => {
    // The app only looks for today's activity among the sessions on page 1, so these get the latest possible
    // start date to be the newest sessions on the site.
    const setup = { visible: true, committees: [{ name: 'ENVI' }, { name: 'AFCO' }], active_debate: 'ENVI' };
    const newest = { start_date: '9999-12-30', end_date: '9999-12-31' };
    const active = await createSession({ ...setup, ...newest });
    const quiet = await createSession({ ...setup, ...newest });
    await addSessionData(active.id, { points: [{ committee: 'AFCO' }] });

    await page.goto('/');
    const activity = (name: string) => page.getByRole('heading', { name: `${name}'s latest activity was` });
    await expect(activity(active.name)).toBeVisible();
    await expect(activity(active.name).getByRole('link', { name: active.name })).toHaveAttribute(
      'href',
      `/session/${active.id}/`,
    );
    await expect(sessionCards(page).filter({ hasText: quiet.name })).toBeVisible();
    await expect(activity(quiet.name)).toHaveCount(0);
  });

  test('lists sessions newest first, 12 per page', async ({ page, createSession }) => {
    // 13 sessions on consecutive days, created oldest to newest. Other tests' sessions may sit between them,
    // so this checks that ours come out newest first across pages and that only the last page is short.
    const ours: string[] = [];
    for (let day = 1; day <= 13; day++) {
      const date = `2800-01-${String(day).padStart(2, '0')}`;
      const session = await createSession({ visible: true, start_date: date, end_date: '2800-01-31' });
      ours.unshift(session.name);
    }

    const cards = sessionCards(page);
    const seen: string[] = [];

    await page.goto('/');
    for (let pageNumber = 2; seen.length < ours.length; pageNumber++) {
      await expect(cards.first()).toBeVisible();
      const names = (await cards.allTextContents()).map((name) => name.trim());
      seen.push(...names.filter((name) => ours.includes(name)));
      if (seen.length < ours.length) {
        expect(names, 'every page before the last is full').toHaveLength(12);
        await page.getByRole('link', { name: 'Older events' }).click();
        await expect(page).toHaveURL(new RegExp(`\\?page=${pageNumber}$`));
      }
    }

    expect(seen).toEqual(ours);
  });
});
