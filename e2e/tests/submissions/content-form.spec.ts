import { expect, test } from '../../support/fixtures';
import { committeeId, debateSetup, liveUpdate, openAsChair, openDebatePage } from './submission-session';

test.describe('content form', () => {
  test('Point Content Only: a point from one committee shows in the debate page point list', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ ...debateSetup, mode: 'C' });
    const content = 'We must cut emissions faster';

    await openAsChair(page, session, `content/${committeeId(session, 'AFCO')}/`);
    await page.getByLabel('Point Type').selectOption('Point');
    await page.getByLabel('Content').fill(content);
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Content Point Successfully Submitted')).toBeVisible();

    await openDebatePage(page, session);
    const row = page.getByRole('row').filter({ hasText: content });
    await expect(row).toBeVisible(liveUpdate);
    await expect(row.getByRole('cell', { name: 'AFCO', exact: true })).toBeVisible();
  });

  test('Point Content Only: the all-committees form saves and returns to the form', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ ...debateSetup, mode: 'C' });
    const content = 'Energy prices matter';

    await openAsChair(page, session, 'content/all/');
    await page.getByLabel('Committee').selectOption('ITRE');
    await page.getByLabel('Content').fill(content);
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Content Point Successfully Submitted')).toBeVisible();
    await expect(page).toHaveURL(`/session/${session.id}/content/all/`);

    await openDebatePage(page, session);
    const row = page.getByRole('row').filter({ hasText: content });
    await expect(row).toBeVisible(liveUpdate);
    await expect(row.getByRole('cell', { name: 'ITRE', exact: true })).toBeVisible();
  });

  test('Split Form: points and content submitted separately both appear on the debate page', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ ...debateSetup, mode: 'SF' });
    const afco = committeeId(session, 'AFCO');
    const content = 'Elections need protecting';

    await openAsChair(page, session, `point/${afco}/`);
    await page.getByLabel('Subtopics Addressed').selectOption('Energy');
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Point Successfully Submitted')).toBeVisible();

    await page.goto(`/session/${session.id}/content/${afco}/`);
    await page.getByLabel('Content').fill(content);
    await page.getByRole('button', { name: 'Submit' }).click();
    await expect(page.getByText('Content Point Successfully Submitted')).toBeVisible();

    await openDebatePage(page, session);
    await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible(liveUpdate);
    await expect(page.getByRole('row').filter({ hasText: content })).toBeVisible(liveUpdate);
  });
});
