import type { Page } from '@playwright/test';
import { addSessionData, type CreatedSession } from '../../support/e2e-api/sessions';
import { loginAs } from '../../support/e2e-api/login';
import { expect, test } from '../../support/fixtures';

// Chairs and journalists submit from their phones, and delegates follow the debate page on theirs.
test.use({ viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true });

async function expectNoHorizontalScroll(page: Page) {
  const { scrollWidth, viewportWidth } = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    viewportWidth: window.innerWidth,
  }));
  expect(scrollWidth, 'page is wider than the screen').toBeLessThanOrEqual(viewportWidth);
}

const committees = [
  { name: 'ENVI', topic: 'Climate topic about emissions', subtopics: ['Emissions'] },
  { name: 'AFCO', topic: 'Constitutional affairs topic' },
];

async function sessionWithData(createSession: (input?: object) => Promise<CreatedSession>) {
  const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });
  await addSessionData(session.id, {
    points: [{ committee: 'AFCO', subtopics: ['Emissions'] }],
    content: [{ committee: 'AFCO', text: 'A point long enough to wrap onto several lines on a narrow phone screen' }],
    votes: [{ committee: 'AFCO', in_favour: 6, against: 2 }],
  });
  return session;
}

test.describe('on a phone', () => {
  test('the session page fits the screen', async ({ page, createSession }) => {
    const session = await sessionWithData(createSession);
    await page.goto(`/session/${session.id}/`);
    await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible({ timeout: 15_000 });
    await expectNoHorizontalScroll(page);
  });

  test('the debate page fits the screen', async ({ page, createSession }) => {
    const session = await sessionWithData(createSession);
    await page.goto(`/session/${session.id}/debate/${session.committees[0].id}/`);
    await expect(page.getByRole('row', { name: /A point long enough to wrap/ })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByRole('heading', { name: 'Votes Counted: 8' })).toBeVisible({ timeout: 15_000 });
    await expectNoHorizontalScroll(page);
  });

  test('the joint form fits the screen and can be submitted', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    await loginAs(page, session.id, 'submission');

    await page.goto(`/session/${session.id}/joint/${session.committees[1].id}/`);
    await expectNoHorizontalScroll(page);
    await expect(page.getByRole('button', { name: /submit/i })).toBeVisible();
  });

  test('the vote form fits the screen and can be submitted', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    await loginAs(page, session.id, 'submission');

    await page.goto(`/session/${session.id}/vote/${session.committees[1].id}/`);
    await expectNoHorizontalScroll(page);
    await expect(page.getByRole('button', { name: /submit/i })).toBeVisible();
  });
});
