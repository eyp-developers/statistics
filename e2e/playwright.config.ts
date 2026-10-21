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

  // Every test sets up its own data and never assumes anything about the rest of the database, so all of them
  // run in parallel against one server, local or shared.
  use: {
    ...devices['Desktop Chrome'],
    baseURL: env.baseURL,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },

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
