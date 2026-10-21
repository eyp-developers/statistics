import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

const committees = [
  { name: 'ENVI', topic: 'Climate topic about emissions' },
  { name: 'AFCO', topic: 'Constitutional affairs topic' },
];

test.describe('session page', () => {
  test('announces the debate that is running today', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    // The banner only shows once the session has had activity today.
    await addSessionData(session.id, { points: [{ committee: 'AFCO' }] });

    await page.goto(`/session/${session.id}/`);
    const banner = page.getByRole('heading', { name: 'ENVI is being debated right now!' });
    await expect(banner).toBeVisible();

    await banner.getByRole('link', { name: 'ENVI' }).click();
    await expect(page).toHaveURL(new RegExp(`/session/${session.id}/debate/${session.committees[0].id}/$`));
  });

  test('shows no debate banner before the GA has started', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });

    await page.goto(`/session/${session.id}/`);
    await expect(page.getByText(`${session.name}'s GA hasn't started yet!`)).toBeVisible();
    await expect(page.getByRole('heading', { name: /is being debated right now!/ })).toHaveCount(0);
  });

  test('warns about missing data when the session had technical problems', async ({ page, createSession }) => {
    const warning = 'Please note that this session experienced technical difficulties during the GA.';

    const withProblems = await createSession({ visible: true, committees, technical_problems: true });
    await page.goto(`/session/${withProblems.id}/`);
    await expect(page.getByText(warning)).toBeVisible();

    const withoutProblems = await createSession({ visible: true, committees });
    await page.goto(`/session/${withoutProblems.id}/`);
    await expect(page.getByText(warning)).toHaveCount(0);
  });

  test("lists each committee with its topic and a link to its debate", async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees });

    await page.goto(`/session/${session.id}/`);
    await expect(page.getByRole('heading', { name: session.name, level: 1 })).toBeVisible();

    for (const committee of session.committees) {
      const topic = committees.find((c) => c.name === committee.name)!.topic;
      await expect(page.getByText(topic)).toBeVisible();
      await expect(page.getByRole('link', { name: committee.name, exact: true })).toHaveAttribute(
        'href',
        `/session/${session.id}/debate/${committee.id}/`,
      );
    }

    await page.getByRole('link', { name: 'AFCO', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'AFCO', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Constitutional affairs topic' })).toBeVisible();
  });
});
