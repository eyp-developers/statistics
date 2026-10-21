import { defineConfig, devices } from '@playwright/test';
import { env } from './support/env';

/**
 * Runs against E2E_BASE_URL when it is set (e.g. a deployed preview with the /__e2e__/ endpoints enabled).
 * Otherwise starts a local server with a fresh database via start-server.sh.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : [['list'], ['html', { open: 'never' }]],

  use: {
    baseURL: env.baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'parallel',
      grepInvert: /@fresh-db/,
      use: { ...devices['Desktop Chrome'] },
    },
    {
      // Tests that look at the whole site (empty home page, pagination, high scores). Each one empties the
      // database first, so they run after everything else, one at a time, and are skipped on targets that
      // don't allow a reset.
      name: 'fresh-db',
      grep: /@fresh-db/,
      dependencies: ['parallel'],
      workers: 1,
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: env.isLocal
    ? {
        command: './start-server.sh',
        url: `${env.baseURL}/`,
        reuseExistingServer: false,
        timeout: 120_000,
        env: {
          E2E_TOKEN: env.token,
          E2E_PORT: String(env.localPort),
          // The create form stores naive datetimes, which floods the output with RuntimeWarnings.
          PYTHONWARNINGS: 'ignore::RuntimeWarning',
        },
        stdout: 'ignore',
        stderr: 'pipe',
      }
    : undefined,
});
