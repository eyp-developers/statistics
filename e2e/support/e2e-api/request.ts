import { env } from '../env';

export const tokenHeader = { 'X-E2E-Token': env.token };

/** Calls a /__e2e__/ endpoint on the target and returns its JSON (or undefined for 204). */
export async function e2eRequest<T = unknown>(method: string, path: string, body?: unknown): Promise<T> {
  const url = `${env.baseURL}/__e2e__/${path}`;
  const response = await fetch(url, {
    method,
    headers: { ...tokenHeader, 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  // The endpoints answer 404 for everything when they are switched off or the token doesn't match.
  if (response.status === 404) {
    throw new Error(
      `The /__e2e__/ endpoints are not available at ${env.baseURL}. ` +
        'Start the server with E2E_ENDPOINTS_ENABLED=true and the same E2E_TOKEN as the tests.',
    );
  }
  if (!response.ok) {
    throw new Error(`${method} ${url} failed: ${response.status} ${(await response.text()).slice(0, 500)}`);
  }
  return response.status === 204 ? (undefined as T) : ((await response.json()) as T);
}
