import type { Page } from '@playwright/test';
import { loginAs } from '../../support/e2e-api/login';
import type { CreatedSession } from '../../support/e2e-api/sessions';

/** Three committees, ENVI being debated, so every submission form has committees, subtopics and an active debate. */
export const debateSetup = {
  visible: true,
  active_debate: 'ENVI',
  active_round: 1,
  committees: [
    { name: 'ENVI', topic: 'Climate and emissions', subtopics: ['Emissions', 'Energy'] },
    { name: 'AFCO', topic: 'Constitutional affairs', subtopics: ['Democracy'] },
    { name: 'ITRE', topic: 'Industry and research', subtopics: ['Chips'] },
  ],
};

export function committeeId(session: CreatedSession, name: string): number {
  const committee = session.committees.find((c) => c.name === name);
  if (!committee) {
    throw new Error(`Session ${session.name} has no committee ${name}`);
  }
  return committee.id;
}

/** Logs in as the session's submission account (the one chairs use) and opens a page of the session. */
export async function openAsChair(page: Page, session: CreatedSession, path: string): Promise<void> {
  await loginAs(page, session.id, 'submission');
  await page.goto(`/session/${session.id}/${path}`);
}

/** The public debate page of a committee, where the submitted statistics show up. */
export async function openDebatePage(page: Page, session: CreatedSession, debate = 'ENVI'): Promise<void> {
  await page.goto(`/session/${session.id}/debate/${committeeId(session, debate)}/`);
}

/** The debate pages poll their data every few seconds. */
export const liveUpdate = { timeout: 15_000 };
