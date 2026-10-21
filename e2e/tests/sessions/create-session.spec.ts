import path from 'node:path';
import type { Page } from '@playwright/test';
import { setSessionState, uniqueSessionName } from '../../support/e2e-api/sessions';
import { closeDatePickers } from '../../support/datepicker';
import { expect, test } from '../../support/fixtures';

const picturePath = path.join(import.meta.dirname, '../../assets/session.jpg');

async function fillCreateSessionForm(page: Page, name: string, dates = { start: '2026-07-17', end: '2026-07-26' }) {
  await page.goto('/create_session/');
  await page.getByLabel('Name', { exact: true }).fill(name);
  await page.getByLabel('Description', { exact: true }).fill('End-to-end test session of the EYP');
  await page.getByLabel('Email', { exact: true }).fill('e2e@example.com');
  await page.getByLabel('Country', { exact: true }).selectOption('DE');
  await page.getByLabel('Picture', { exact: true }).setInputFiles(picturePath);
  await page.getByLabel('Start date', { exact: true }).fill(dates.start);
  await page.getByLabel('End date', { exact: true }).fill(dates.end);
  await closeDatePickers(page);
  await page.getByLabel('Statistics', { exact: true }).selectOption('Joint Form Statistics');
  await page.getByLabel('Max rounds', { exact: true }).fill('3');
  await page.getByLabel('Admin password', { exact: true }).fill('admin-password');
  await page.getByLabel('Submission password', { exact: true }).fill('submission-password');
}

/** The session ID from the overview page's URL, /overview/<id>/. */
async function sessionIdFromOverview(page: Page): Promise<number> {
  await expect(page).toHaveURL(/\/overview\/\d+\/$/);
  return Number(page.url().match(/\/overview\/(\d+)\/$/)![1]);
}

test.describe('creating a session', () => {
  test('creates the session, shows its logins and signs in as its admin', async ({ page, cleanUpSession }) => {
    const name = uniqueSessionName();
    await fillCreateSessionForm(page, name);
    await page.getByRole('button', { name: 'Create Session' }).click();

    const sessionId = await sessionIdFromOverview(page);
    cleanUpSession(sessionId);

    // The app derives both usernames from the name with spaces removed, lowercased.
    const username = name.replace(/\s+/g, '').toLowerCase();
    await expect(page.getByRole('heading', { name: `Welcome to GA Statistics, ${name}` })).toBeVisible();
    await expect(page.getByRole('heading', { name: `Your Admin Username is ${username}_admin` })).toBeVisible();
    await expect(page.getByRole('heading', { name: `Your Submission Username is ${username}` })).toBeVisible();

    // Creating a session logs the creator in as its admin, so admin-only pages open without the login form.
    await page.goto(`/edit/${sessionId}/`);
    await expect(page).toHaveURL(new RegExp(`/edit/${sessionId}/$`));
    await expect(page).toHaveTitle(`Edit - ${name} | GA Statistics`);
  });

  test('new sessions are hidden from the home page until made visible', async ({ page, cleanUpSession }) => {
    const name = uniqueSessionName();
    // The home page lists sessions newest first, 12 per page. A start date far in the future keeps this one
    // on page 1 while other tests create sessions in parallel.
    await fillCreateSessionForm(page, name, { start: '2099-12-01', end: '2099-12-10' });
    await page.getByRole('button', { name: 'Create Session' }).click();

    const sessionId = await sessionIdFromOverview(page);
    cleanUpSession(sessionId);
    await expect(page.getByText("Your session isn't visible to the public yet.")).toBeVisible();

    // Each session on the home page is a card headed by the session's name.
    const sessionCard = page.getByRole('heading', { name, exact: true });
    await page.goto('/');
    await expect(sessionCard).toBeHidden();

    // Making it visible shows the card, which also proves the check above looked in the right place.
    await setSessionState(sessionId, { visible: true });
    await page.reload();
    await expect(sessionCard).toBeVisible();
  });

  test('rejects a name that is already taken, even with different spacing or case', async ({ page, createSession }) => {
    const existing = await createSession();

    for (const name of [existing.name, existing.name.replace(/\s+/g, '').toUpperCase()]) {
      await test.step(`"${name}"`, async () => {
        await fillCreateSessionForm(page, name);
        await page.getByRole('button', { name: 'Create Session' }).click();

        await expect(page.getByText('Session with this name or a similar name already exists')).toBeVisible();
        await expect(page).toHaveURL(/\/create_session\/$/);
      });
    }
  });

  test('invalid details are rejected and create no session', async ({ page, cleanUpSession }) => {
    const name = uniqueSessionName();
    const invalidCases = [
      { what: 'missing picture', label: 'Picture', breakIt: (p: Page) => p.getByLabel('Picture', { exact: true }).setInputFiles([]), error: 'This field is required.' },
      { what: 'bad email', label: 'Email', breakIt: (p: Page) => p.getByLabel('Email', { exact: true }).fill('not-an-email'), error: 'Enter a valid email address.' },
      { what: 'max rounds below 1', label: 'Max rounds', breakIt: (p: Page) => p.getByLabel('Max rounds', { exact: true }).fill('0'), error: 'Ensure this value is greater than or equal to 1.' },
      { what: 'max rounds above 10', label: 'Max rounds', breakIt: (p: Page) => p.getByLabel('Max rounds', { exact: true }).fill('11'), error: 'Ensure this value is less than or equal to 10.' },
    ];

    for (const invalid of invalidCases) {
      await test.step(invalid.what, async () => {
        await fillCreateSessionForm(page, name);
        await invalid.breakIt(page);
        const submit = page.getByRole('button', { name: 'Create Session' });

        // The browser's own validation stops the form from being sent...
        await submit.click();
        await expect(page).toHaveURL(/\/create_session\/$/);
        const field = page.getByLabel(invalid.label, { exact: true });
        expect(await field.evaluate((el) => (el as HTMLInputElement).validity.valid)).toBe(false);

        // ...and the server rejects it too, for clients that skip the browser checks.
        await submit.evaluate((button) => {
          (button as HTMLButtonElement).form!.noValidate = true;
        });
        await submit.click();
        await expect(page).toHaveURL(/\/create_session\/$/);
        await expect(page.getByText(invalid.error)).toBeVisible();
      });
    }

    // None of the attempts created the session: the same name is still free.
    await fillCreateSessionForm(page, name);
    await page.getByRole('button', { name: 'Create Session' }).click();
    cleanUpSession(await sessionIdFromOverview(page));
  });
});
