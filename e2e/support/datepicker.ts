import type { Page } from '@playwright/test';

/**
 * The material date pickers on the session create and edit forms open on top of each other as soon as their
 * inputs are focused, and cover the submit button. Close them top-down the way a user would, with OK.
 */
export async function closeDatePickers(page: Page): Promise<void> {
  const openPickers = page.locator('.dtp:visible');
  while ((await openPickers.count()) > 0) {
    await openPickers.last().locator('.dtp-btn-ok').click();
  }
}
