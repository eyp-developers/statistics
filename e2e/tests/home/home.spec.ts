import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

/**
 * The home page lists visible sessions newest first, 12 per page, and other tests create sessions in parallel
 * (some with start dates years ahead). A start date centuries ahead keeps this test's session on page 1.
 */
function farFutureDates() {
  const day = String(1 + Math.floor(Math.random() * 27)).padStart(2, '0');
  const month = String(1 + Math.floor(Math.random() * 12)).padStart(2, '0');
  return { start_date: `2900-${month}-${day}`, end_date: `2900-${month}-28` };
}

test.describe('home page', () => {
  test("links each visible session's card to its session page", async ({ page, createSession }) => {
    const session = await createSession({ visible: true, ...farFutureDates() });

    await page.goto('/');
    // Each card is a link headed by the session's name.
    await page.getByRole('heading', { name: session.name, exact: true }).click();

    await expect(page).toHaveURL(new RegExp(`/session/${session.id}/$`));
    await expect(page.getByRole('heading', { name: session.name, level: 1 })).toBeVisible();
  });

  test('flags sessions with activity today', async ({ page, createSession }) => {
    const committees = [{ name: 'ENVI' }, { name: 'AFCO' }];
    const active = await createSession({ visible: true, committees, active_debate: 'ENVI', ...farFutureDates() });
    const quiet = await createSession({ visible: true, committees, active_debate: 'ENVI', ...farFutureDates() });
    await addSessionData(active.id, { points: [{ committee: 'AFCO' }] });

    await page.goto('/');
    const activity = (name: string) => page.getByRole('heading', { name: `${name}'s latest activity was` });
    await expect(activity(active.name)).toBeVisible();
    await expect(activity(active.name).getByRole('link', { name: active.name })).toHaveAttribute(
      'href',
      `/session/${active.id}/`,
    );
    await expect(page.getByRole('heading', { name: quiet.name, exact: true })).toBeVisible();
    await expect(activity(quiet.name)).toHaveCount(0);
  });
});
