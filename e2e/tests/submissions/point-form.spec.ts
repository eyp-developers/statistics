import { expect, test } from '../../support/fixtures';
import { committeeId, debateSetup, liveUpdate, openAsChair, openDebatePage } from './submission-session';

test.describe('point form', () => {
  test('Statistics Only: points from one committee and from the all-committees form count on the debate page', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ ...debateSetup, mode: 'S' });

    await test.step('one committee', async () => {
      await openAsChair(page, session, `point/${committeeId(session, 'AFCO')}/`);
      await expect(page.getByRole('heading', { name: 'Submit point from AFCO on ENVI' })).toBeVisible();
      await page.getByLabel('Point Type').selectOption('Point');
      await page.getByLabel('Subtopics Addressed').selectOption('Emissions');
      await page.getByRole('button', { name: 'Submit' }).click();
      await expect(page.getByText('Point Successfully Submitted')).toBeVisible();
    });

    await test.step('all committees', async () => {
      await page.goto(`/session/${session.id}/point/all/`);
      await page.getByLabel('Committee').selectOption('ITRE');
      await expect(page.getByLabel('Debate')).toHaveValue('ENVI');
      await page.getByLabel('Point Type').selectOption('Direct Response');
      // The all-committees form lists every subtopic as "<subtopic> - <committee>".
      await page.getByLabel('Subtopics Addressed').selectOption('Energy - ENVI');
      await page.getByRole('button', { name: 'Submit' }).click();
      await expect(page).toHaveURL(new RegExp(`/session/${session.id}/point/all/$`));
      await expect(page.getByText('Point Successfully Submitted')).toBeVisible();
    });

    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'Total Points: 2' })).toBeVisible(liveUpdate);
    await expect(page.getByText('(1 Points, 1 Direct Responses)')).toBeVisible(liveUpdate);
    await expect(page.getByRole('heading', { name: 'Latest Point By: ITRE' })).toBeVisible(liveUpdate);
  });

  test('Running Order Statistics: the point form works and the debate page renders it', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ ...debateSetup, mode: 'R' });

    await openAsChair(page, session, `point/${committeeId(session, 'ITRE')}/`);
    await page.getByLabel('Subtopics Addressed').selectOption('General');
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Point Successfully Submitted')).toBeVisible();

    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'ENVI', level: 1 })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible(liveUpdate);
  });
});
