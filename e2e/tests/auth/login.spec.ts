import type { Page } from '@playwright/test';
import { expect, test } from '../../support/fixtures';

async function logInWithForm(page: Page, username: string, password: string) {
  await page.getByLabel('Username').fill(username);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Submit' }).click();
}

test.describe('logging in', () => {
  test('the session admin lands on their own session page', async ({ page, createSession }) => {
    const session = await createSession();

    await page.goto('/login/');
    await logInWithForm(page, session.admin.username, session.admin.password);

    await expect(page).toHaveURL(new RegExp(`/session/${session.id}/$`));
    await expect(page.getByText(`Welcome ${session.admin.username}, you have been logged in.`)).toBeVisible();
  });

  test('the submission account lands on the session page', async ({ page, createSession }) => {
    const session = await createSession();

    await page.goto('/login/');
    await logInWithForm(page, session.submission.username, session.submission.password);

    await expect(page).toHaveURL(new RegExp(`/session/${session.id}/$`));
    await expect(page.getByText(`Welcome ${session.submission.username}, you have been logged in.`)).toBeVisible();
  });

  test('returns to the page that asked for a login', async ({ page, createSession }) => {
    const session = await createSession();

    await page.goto(`/manage/${session.id}/`);
    await expect(page).toHaveURL(`/login/?next=/manage/${session.id}/`);
    await logInWithForm(page, session.admin.username, session.admin.password);

    await expect(page).toHaveURL(new RegExp(`/manage/${session.id}/$`));
    await expect(page).toHaveTitle(`Manage: ${session.name} | GA Statistics`);
  });

  test('a wrong password is rejected', async ({ page, createSession }) => {
    const session = await createSession();

    await page.goto('/login/');
    await logInWithForm(page, session.admin.username, 'not-the-password');

    await expect(page).toHaveURL(/\/login\/$/);
    await expect(page.getByText('This username password combination does not exist.')).toBeVisible();
  });
});

test('logging out ends the session', async ({ page, createSession }) => {
  const session = await createSession();
  await page.goto('/login/');
  await logInWithForm(page, session.admin.username, session.admin.password);
  await expect(page).toHaveURL(new RegExp(`/session/${session.id}/$`));

  await page.goto('/logout/');
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByText('You are now logged out.')).toBeVisible();

  // Admin pages need a login again.
  await page.goto(`/edit/${session.id}/`);
  await expect(page).toHaveURL(`/login/?next=/edit/${session.id}/`);
});
