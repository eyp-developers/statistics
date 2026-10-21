import { expect, type Locator, type Page } from '@playwright/test';

/** Session cards on the current home page; each is a link headed by the session's name. */
export function sessionCards(page: Page): Locator {
  return page.getByRole('region', { name: 'Sessions' }).getByRole('heading', { level: 1 });
}

/**
 * Opens the home page and follows "Older events" until the session's card shows up. Returns the card, or null
 * once the last page is reached without it. Other tests create sessions at the same time, so a session can be on
 * any page.
 */
export async function findSessionCard(page: Page, sessionName: string): Promise<Locator | null> {
  await page.goto('/');
  const card = sessionCards(page).filter({ hasText: sessionName });
  const olderEvents = page.getByRole('link', { name: 'Older events' });

  for (let pageNumber = 2; ; pageNumber++) {
    if (await card.isVisible()) {
      return card;
    }
    if (!(await olderEvents.isVisible())) {
      return null;
    }
    await olderEvents.click();
    await expect(page).toHaveURL(new RegExp(`\\?page=${pageNumber}$`));
  }
}
