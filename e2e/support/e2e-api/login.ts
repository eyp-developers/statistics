import { expect, type Page } from '@playwright/test';
import { tokenHeader } from './request';

export type Role = 'admin' | 'submission';

/**
 * Logs the page in as a session's admin or submission account, without going through the login form.
 * Uses page.request rather than fetch because it shares cookies with the page, so the login sticks.
 */
export async function loginAs(page: Page, sessionId: number, role: Role): Promise<void> {
  const response = await page.request.post('/__e2e__/login/', {
    headers: tokenHeader,
    data: { session_id: sessionId, role },
  });
  expect(response.ok(), `Logging in as ${role} of session ${sessionId}`).toBeTruthy();
}
