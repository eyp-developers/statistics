import type { Page } from '@playwright/test';
import { loginAs } from '../../support/e2e-api/login';
import { addSessionData } from '../../support/e2e-api/sessions';
import { expect, test } from '../../support/fixtures';

/** Posts a form to the app the way a script on another tab could: with a CSRF cookie from the login page. */
async function postWithCsrf(page: Page, path: string, form: Record<string, string | number>) {
  await page.goto('/login/');
  const csrf = (await page.context().cookies()).find((cookie) => cookie.name === 'csrftoken')!;
  return page.request.post(path, { form, headers: { 'X-CSRFToken': csrf.value, Referer: page.url() } });
}

async function readVote(page: Page, pk: number) {
  const response = await page.request.get(`/api/pk_data/?data_type=vote&pk=${pk}`);
  expect(response.ok()).toBeTruthy();
  return response.json();
}

test.describe('data-editing APIs', () => {
  test("a logged-out visitor can't delete or edit a vote", async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    const { votes } = await addSessionData(session.id, { votes: [{ committee: 'AFCO', in_favour: 10, against: 3 }] });

    const deletion = await postWithCsrf(page, '/api/pk_data/', { delete: 'true', 'data-type': 'vote', pk: votes[0] });
    expect(deletion.status()).toBe(403);

    const edit = await postWithCsrf(page, '/api/pk_data/', {
      'data-type': 'vote',
      pk: votes[0],
      session: session.id,
      committee: 'AFCO',
      debate: 'ENVI',
      in_favour: 0,
      against: 0,
      abstentions: 0,
      absent: 0,
    });
    expect(edit.status()).toBe(403);

    expect(await readVote(page, votes[0])).toMatchObject({ pk: votes[0], in_favour: 10, against: 3 });
  });

  test("another session's admin can't delete a vote", async ({ page, createSession }) => {
    const session = await createSession({ active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    const otherSession = await createSession();
    const { votes } = await addSessionData(session.id, { votes: [{ committee: 'AFCO', in_favour: 10 }] });
    await loginAs(page, otherSession.id, 'admin');

    const deletion = await postWithCsrf(page, '/api/pk_data/', { delete: 'true', 'data-type': 'vote', pk: votes[0] });
    expect(deletion.status()).toBe(403);
    expect(await readVote(page, votes[0])).toMatchObject({ in_favour: 10 });
  });

  test("a logged-out visitor can't change the running order", async ({ page, createSession }) => {
    const session = await createSession({ mode: 'R', active_debate: 'ENVI', committees: [{ name: 'ENVI' }, { name: 'AFCO' }] });
    const afco = session.committees.find((c) => c.name === 'AFCO')!;

    const add = await postWithCsrf(page, `/api/runningorder/${session.id}/`, { by: afco.id, type: 'P' });
    expect(add.status()).toBe(403);

    const order = await page.request.get(`/api/runningorder/${session.id}/`);
    expect((await order.json()).queue).toEqual([]);
  });
});
