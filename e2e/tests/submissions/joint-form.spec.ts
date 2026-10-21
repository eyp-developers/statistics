import { expect, test } from '../../support/fixtures';
import type { StatisticsMode } from '../../support/e2e-api/sessions';
import { committeeId, debateSetup, liveUpdate, openAsChair, openDebatePage } from './submission-session';

const modes: { mode: StatisticsMode; label: string }[] = [
  { mode: 'JF', label: 'Joint Form' },
  { mode: 'RC', label: 'Running Order with Content' },
];

for (const { mode, label } of modes) {
  test(`${label}: the joint form records the point and its content on the debate page`, async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ ...debateSetup, mode });

    await test.step('one committee', async () => {
      await openAsChair(page, session, `joint/${committeeId(session, 'AFCO')}/`);
      await expect(page.getByRole('heading', { name: 'Submit statistics from AFCO on ENVI' })).toBeVisible();
      await page.getByLabel('Point Type').selectOption('Point');
      await page.getByLabel('Subtopics Addressed').selectOption(['Emissions', 'Energy']);
      await page.getByLabel('Content').fill('We must cut emissions faster');
      await page.getByRole('button', { name: 'Submit' }).click();
      await expect(page.getByText('Point Successfully Submitted')).toBeVisible();
    });

    await test.step('all committees', async () => {
      await page.goto(`/session/${session.id}/joint/all/`);
      await page.getByLabel('Committee').selectOption('ITRE');
      await page.getByLabel('Point Type').selectOption('Direct Response');
      await page.getByLabel('Subtopics Addressed').selectOption('General - ENVI');
      await page.getByLabel('Content').fill('Energy prices matter');
      await page.getByRole('button', { name: 'Submit' }).click();
      await expect(page).toHaveURL(new RegExp(`/session/${session.id}/joint/all/$`));
      await expect(page.getByText('Point Successfully Submitted')).toBeVisible();
    });

    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'Total Points: 2' })).toBeVisible(liveUpdate);
    await expect(page.getByText('(1 Points, 1 Direct Responses)')).toBeVisible(liveUpdate);
    await expect(page.getByRole('row').filter({ hasText: 'We must cut emissions faster' })).toBeVisible(liveUpdate);
    await expect(page.getByRole('row').filter({ hasText: 'Energy prices matter' })).toBeVisible(liveUpdate);
  });
}
