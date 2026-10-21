import type { Page } from '@playwright/test';
import { loginAs } from '../../support/e2e-api/login';
import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

// Text that delegates and chairs type in must show up as text, not run as HTML in every viewer's browser.
const payload = (marker: string) => `<img src=x onerror="window.${marker}=1">`;
const pointText = payload('__xssContent');
const subtopicName = payload('__xssSubtopic');

const committees = [{ name: 'ENVI', subtopics: [subtopicName] }, { name: 'AFCO' }];

async function injectedMarkers(page: Page) {
  return page.evaluate(() => {
    const w = window as unknown as Record<string, unknown>;
    return { content: w.__xssContent, subtopic: w.__xssSubtopic };
  });
}

test.describe('user-submitted text', () => {
  test('point content is shown as literal text on the debate page', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    const envi = session.committees.find((c) => c.name === 'ENVI')!;
    await addSessionData(session.id, { content: [{ committee: 'AFCO', text: pointText }] });

    await page.goto(`/session/${session.id}/debate/${envi.id}/`);

    await expect(page.getByRole('table').getByText(pointText, { exact: true })).toBeVisible({ timeout: 15_000 });
    expect(await injectedMarkers(page)).toEqual({ content: undefined, subtopic: undefined });
  });

  test('point content and subtopic names are shown as literal text on the manage page', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ committees, active_debate: 'ENVI' });
    await addSessionData(session.id, {
      points: [{ committee: 'AFCO', subtopics: [subtopicName] }],
      content: [{ committee: 'AFCO', text: pointText }],
    });
    await loginAs(page, session.id, 'admin');

    await page.goto(`/manage/${session.id}/`);

    await expect(page.getByRole('cell', { name: pointText, exact: true })).toBeVisible();
    await expect(page.getByRole('cell', { name: subtopicName, exact: true })).toBeVisible();
    expect(await injectedMarkers(page)).toEqual({ content: undefined, subtopic: undefined });
  });
});
