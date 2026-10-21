import { loginAs } from '../../support/e2e-api/login';
import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

// A Joint Form session debating ENVI, so the manage page shows points, content points and votes.
const committees = [{ name: 'ENVI', subtopics: ['Emissions'] }, { name: 'AFCO' }, { name: 'ITRE' }];

test.describe('editing submitted data on the manage page', () => {
  test('editing a point changes it on the debate page', async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees });
    const envi = session.committees.find((c) => c.name === 'ENVI')!;
    const { points } = await addSessionData(session.id, { points: [{ committee: 'AFCO', subtopics: ['Emissions'] }] });
    await loginAs(page, session.id, 'admin');
    await page.goto(`/manage/${session.id}/`);

    await page.getByRole('link', { name: `Edit point ${points[0]}` }).click();
    const dialog = page.getByRole('dialog', { name: 'Edit point' });
    // The dialog is filled in from the API; wait for it before changing anything.
    await expect(dialog.getByLabel('Committee:')).toHaveValue('AFCO');
    await dialog.getByLabel('Committee:').selectOption('ITRE');
    await dialog.getByLabel('Round Number:').selectOption('2');
    await dialog.getByRole('button', { name: 'Save Point' }).click();

    await expect(page.getByText('Point Saved')).toBeVisible();
    const row = page.getByRole('row').filter({ has: page.getByRole('link', { name: `Edit point ${points[0]}` }) });
    await expect(row).toContainText('ITRE');
    await expect(row).toContainText('Emissions');

    await page.goto(`/session/${session.id}/debate/${envi.id}/`);
    await expect(page.getByRole('heading', { name: 'Latest Point By: ITRE' })).toBeVisible({ timeout: 15_000 });
  });

  test('editing a content point and a vote changes them on the debate page', async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees });
    const envi = session.committees.find((c) => c.name === 'ENVI')!;
    const created = await addSessionData(session.id, {
      content: [{ committee: 'AFCO', text: 'The original point' }],
      votes: [{ committee: 'AFCO', in_favour: 10, against: 3, abstentions: 1 }],
    });
    await loginAs(page, session.id, 'admin');
    await page.goto(`/manage/${session.id}/`);

    await page.getByRole('link', { name: `Edit content point ${created.content[0]}` }).click();
    const contentDialog = page.getByRole('dialog', { name: 'Edit content point' });
    await expect(contentDialog.getByLabel('Content:')).toHaveValue('The original point');
    await contentDialog.getByLabel('Content:').fill('The corrected point');
    await contentDialog.getByRole('button', { name: 'Save Content Point' }).click();
    await expect(page.getByText('Content Point Saved')).toBeVisible();
    await expect(contentDialog).toBeHidden();

    await page.getByRole('link', { name: `Edit vote ${created.votes[0]}` }).click();
    const voteDialog = page.getByRole('dialog', { name: 'Edit vote' });
    await expect(voteDialog.getByLabel('In Favour:')).toHaveValue('10');
    await voteDialog.getByLabel('In Favour:').fill('12');
    await voteDialog.getByRole('button', { name: 'Save Vote' }).click();
    await expect(page.getByText('Vote Saved')).toBeVisible();

    await page.goto(`/session/${session.id}/debate/${envi.id}/`);
    await expect(page.getByText('The corrected point')).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText('The original point')).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'In Favour: 12' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Votes Counted: 16' })).toBeVisible();
  });

  test('deleting a point, content point and vote removes them from the totals', async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees });
    const envi = session.committees.find((c) => c.name === 'ENVI')!;
    const created = await addSessionData(session.id, {
      points: [{ committee: 'AFCO' }, { committee: 'ITRE' }],
      content: [{ committee: 'AFCO', text: 'A point to delete' }, { committee: 'ITRE', text: 'A point to keep' }],
      votes: [
        { committee: 'AFCO', in_favour: 10, against: 3, abstentions: 1 },
        { committee: 'ITRE', in_favour: 5 },
      ],
    });
    await loginAs(page, session.id, 'admin');
    await page.goto(`/manage/${session.id}/`);

    page.on('dialog', (dialog) => dialog.accept());
    for (const name of [
      `Delete point ${created.points[0]}`,
      `Delete content point ${created.content[0]}`,
      `Delete vote ${created.votes[0]}`,
    ]) {
      await page.getByRole('link', { name }).click();
      await expect(page.getByRole('link', { name })).toHaveCount(0);
    }

    await page.reload();
    await expect(page.getByRole('link', { name: `Delete point ${created.points[1]}` })).toBeVisible();
    await expect(page.getByRole('link', { name: `Delete point ${created.points[0]}` })).toHaveCount(0);

    await page.goto(`/session/${session.id}/debate/${envi.id}/`);
    await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible({ timeout: 15_000 });
    await expect(page.getByText('A point to keep')).toBeVisible();
    await expect(page.getByText('A point to delete')).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Votes Counted: 5' })).toBeVisible();
  });
});
