import { loginAs } from '../../support/e2e-api/login';
import { expect, test } from '../../support/fixtures';

const adminPages = (id: number) => [`/overview/${id}/`, `/edit/${id}/`, `/committees/${id}/`, `/manage/${id}/`];

test.describe('access control', () => {
  test('logged-out visitors are sent to the login page from every protected page', async ({ page, createSession }) => {
    const session = await createSession({ committees: [{ name: 'ENVI' }], active_debate: 'ENVI' });
    const id = session.id;
    const committeeId = session.committees[0].id;

    const protectedPages = [
      ...adminPages(id),
      `/gender/${id}/`,
      `/runningorder/${id}/`,
      ...['point', 'vote', 'content', 'joint'].flatMap((form) => [
        `/session/${id}/${form}/${committeeId}/`,
        `/session/${id}/${form}/all/`,
      ]),
      `/session/${id}/input/${committeeId}/`,
    ];

    for (const path of protectedPages) {
      await test.step(path, async () => {
        await page.goto(path);
        await expect.soft(page).toHaveURL(`/login/?next=${path}`);
      });
    }
  });

  test('the submission account is kept out of admin pages', async ({ page, createSession }) => {
    const session = await createSession();
    await loginAs(page, session.id, 'submission');

    for (const path of [...adminPages(session.id), `/runningorder/${session.id}/`]) {
      await test.step(path, async () => {
        await page.goto(path);
        await expect.soft(page).toHaveURL(/\/login\/$/);
        await expect
          .soft(page.getByText(`You are not authorized to view this page. You need to log in as the ${session.name} admin.`))
          .toBeVisible();
      });
    }
  });

  test("one session's admin can't open another session's admin pages", async ({ page, createSession }) => {
    const sessionA = await createSession();
    const sessionB = await createSession();
    await loginAs(page, sessionA.id, 'admin');

    // A sanity check that the login worked: session A's own pages open.
    await page.goto(`/manage/${sessionA.id}/`);
    await expect(page).toHaveTitle(`Manage: ${sessionA.name} | GA Statistics`);

    for (const path of adminPages(sessionB.id)) {
      await test.step(path, async () => {
        await page.goto(path);
        await expect.soft(page).toHaveURL(/\/login\/$/);
        await expect
          .soft(page.getByText(`You are not authorized to view this page. You need to log in as the ${sessionB.name} admin.`))
          .toBeVisible();
      });
    }
  });
});
