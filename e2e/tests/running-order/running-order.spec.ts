import type { Page } from '@playwright/test';
import { loginAs } from '../../support/e2e-api/login';
import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

// The running order is likely to be removed, so this only checks the page works at all.

/** Opens the running order page and returns the page errors and the status of its first data poll. */
async function openRunningOrder(page: Page, sessionId: number) {
  const pageErrors: Error[] = [];
  page.on('pageerror', (error) => pageErrors.push(error));
  const poll = page.waitForResponse((response) => response.url().includes(`/api/runningorder/${sessionId}/`));
  await page.goto(`/runningorder/${sessionId}/`);
  return { pageErrors, pollStatus: (await poll).status() };
}

test.describe('running order', () => {
  test('loads for a session without points', async ({ page, createSession }) => {
    const session = await createSession({ mode: 'R', active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    await loginAs(page, session.id, 'admin');

    const { pageErrors, pollStatus } = await openRunningOrder(page, session.id);

    await expect(page.getByRole('heading', { name: 'Running Order' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Active Debate: ENVI' })).toBeVisible();
    expect(pollStatus).toBe(200);
    expect(pageErrors).toEqual([]);
  });

  test('loads for a session with points', async ({ page, createSession }) => {
    const session = await createSession({ mode: 'R', active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    await addSessionData(session.id, { points: [{ committee: 'AFCO' }] });
    await loginAs(page, session.id, 'admin');

    const { pageErrors, pollStatus } = await openRunningOrder(page, session.id);

    expect(pollStatus).toBe(200);
    expect(pageErrors).toEqual([]);
  });
});
