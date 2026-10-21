import { addSessionData, type CreatedSession, type StatisticsMode } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

// The debate page polls the API every 1–3 seconds, so give live values time to arrive.
const live = { timeout: 15_000 };

const committees = [
  { name: 'ENVI', topic: 'Climate topic about emissions', subtopics: ['Emissions', 'Energy'] },
  { name: 'AFCO', topic: 'Constitutional affairs topic' },
  { name: 'ITRE', topic: 'Industry and research topic' },
];

function debatePath(session: CreatedSession, committeeName: string): string {
  const committee = session.committees.find((c) => c.name === committeeName)!;
  return `/session/${session.id}/debate/${committee.id}/`;
}

test.describe('debate page', () => {
  test('shows point totals, the latest point, point summaries and the voting summary', async ({
    page,
    createSession,
  }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });
    // Backdated so "latest point" is unambiguous: the ITRE point without minutes_ago is the newest.
    await addSessionData(session.id, {
      points: [
        { committee: 'AFCO', subtopics: ['Emissions'], minutes_ago: 3 },
        { committee: 'ITRE', type: 'DR', subtopics: ['Energy'], minutes_ago: 2 },
        { committee: 'ITRE', subtopics: ['General', 'Emissions'] },
      ],
      content: [
        { committee: 'AFCO', text: 'We must cut emissions faster', minutes_ago: 3 },
        { committee: 'ITRE', text: 'Energy prices matter', type: 'DR', minutes_ago: 2 },
      ],
      votes: [
        { committee: 'AFCO', in_favour: 10, against: 3, abstentions: 1, absent: 0 },
        { committee: 'ITRE', in_favour: 8, against: 5, abstentions: 2, absent: 1 },
      ],
    });

    await page.goto(debatePath(session, 'ENVI'));
    await expect(page.getByRole('heading', { name: 'ENVI', exact: true })).toBeVisible();

    await expect(page.getByRole('heading', { name: 'Total Points: 3' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: '(2 Points, 1 Direct Responses)' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Latest Point By: ITRE' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: /^On: General, Emissions/ })).toBeVisible(live);

    const summaries = page.getByRole('table');
    await expect(summaries.getByRole('row', { name: 'AFCO We must cut emissions faster Point' })).toBeVisible(live);
    await expect(summaries.getByRole('row', { name: 'ITRE Energy prices matter Direct Response' })).toBeVisible(live);

    await expect(page.getByRole('heading', { name: 'Votes Counted: 30' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Committees Counted: 2/3' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'In Favour: 18' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Against: 8' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Abstentions: 3' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Absent: 1' })).toBeVisible(live);
  });

  test('updates live when new points and votes come in, without a reload', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI' });

    await page.goto(debatePath(session, 'ENVI'));
    await expect(page.getByRole('heading', { name: 'Total Points: 0' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Votes Counted: 0' })).toBeVisible(live);

    await addSessionData(session.id, {
      points: [{ committee: 'AFCO', subtopics: ['Energy'] }],
      content: [{ committee: 'AFCO', text: 'A point made while the page was open' }],
      votes: [{ committee: 'AFCO', in_favour: 4, against: 2 }],
    });

    await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Latest Point By: AFCO' })).toBeVisible(live);
    await expect(page.getByRole('row', { name: /A point made while the page was open/ })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Votes Counted: 6' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: 'Committees Counted: 1/3' })).toBeVisible(live);
  });

  test('counts points from every round of the debate', async ({ page, createSession }) => {
    const session = await createSession({ visible: true, committees, active_debate: 'ENVI', max_rounds: 3 });
    await addSessionData(session.id, {
      points: [
        { committee: 'AFCO', round: 1, minutes_ago: 3 },
        { committee: 'ITRE', round: 1, minutes_ago: 2 },
        { committee: 'AFCO', round: 2, type: 'DR', minutes_ago: 1 },
        { committee: 'ITRE', round: 2 },
        // A point in another debate must not count towards this one.
        { committee: 'ENVI', debate: 'AFCO', round: 1 },
      ],
    });

    // The split per round is only drawn in the subtopics chart; as text, the page shows the debate's total.
    await page.goto(debatePath(session, 'ENVI'));
    await expect(page.getByRole('heading', { name: 'Total Points: 4' })).toBeVisible(live);
    await expect(page.getByRole('heading', { name: '(3 Points, 1 Direct Responses)' })).toBeVisible(live);

    await page.goto(debatePath(session, 'AFCO'));
    await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible(live);
  });

  // Which panels each statistics mode shows on the debate page.
  const modes: { mode: StatisticsMode; label: string; charts: boolean; summaries: boolean }[] = [
    { mode: 'S', label: 'Statistics Only', charts: true, summaries: false },
    { mode: 'C', label: 'Point Content Only', charts: false, summaries: true },
    { mode: 'JF', label: 'Joint Form Statistics', charts: true, summaries: true },
    { mode: 'SF', label: 'Split Form Statistics', charts: true, summaries: true },
    { mode: 'R', label: 'Running Order Statistics', charts: true, summaries: false },
    { mode: 'RC', label: 'Running Order Statistics with Point Content', charts: true, summaries: true },
  ];

  for (const { mode, label, charts, summaries } of modes) {
    test(`loads without errors in ${label} mode (${mode})`, async ({ page, createSession }) => {
      const errors: string[] = [];
      page.on('pageerror', (error) => errors.push(error.message));

      const session = await createSession({ visible: true, mode, committees, active_debate: 'ENVI' });
      await addSessionData(session.id, {
        points: [{ committee: 'AFCO' }],
        content: [{ committee: 'AFCO', text: `A ${mode} mode point` }],
        votes: [{ committee: 'AFCO', in_favour: 5, against: 1 }],
      });

      await page.goto(debatePath(session, 'ENVI'));

      const pointsMade = page.getByRole('heading', { name: 'Points Made', exact: true });
      const subtopics = page.getByRole('heading', { name: 'Subtopics and Totals' });
      const pointSummaries = page.getByRole('heading', { name: 'Point Summaries' });

      if (charts) {
        await expect(pointsMade).toBeVisible();
        await expect(subtopics).toBeVisible();
        await expect(page.getByRole('heading', { name: 'Total Points: 1' })).toBeVisible(live);
      } else {
        await expect(pointsMade).toHaveCount(0);
        await expect(subtopics).toHaveCount(0);
      }

      if (summaries) {
        await expect(pointSummaries).toBeVisible();
        await expect(page.getByRole('row', { name: new RegExp(`A ${mode} mode point`) })).toBeVisible(live);
      } else {
        await expect(pointSummaries).toHaveCount(0);
      }

      await expect(page.getByRole('heading', { name: 'Voting Summary' })).toBeVisible();
      await expect(page.getByRole('heading', { name: 'Votes Counted: 6' })).toBeVisible(live);

      expect(errors).toEqual([]);
    });
  }
});
