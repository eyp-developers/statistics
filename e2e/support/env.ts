const localPort = Number(process.env.E2E_PORT ?? 8765);
const baseURL = (process.env.E2E_BASE_URL ?? `http://127.0.0.1:${localPort}`).replace(/\/$/, '');

export const env = {
  baseURL,
  localPort,
  /** True when Playwright starts the server itself (no E2E_BASE_URL given). */
  isLocal: !process.env.E2E_BASE_URL,
  /** Must match the server's E2E_TOKEN. The local server is started with this value. */
  token: process.env.E2E_TOKEN ?? 'local-e2e-token',
  /** Set E2E_KEEP_DATA=1 to keep the sessions tests create, for debugging. */
  keepData: process.env.E2E_KEEP_DATA === '1',
};
