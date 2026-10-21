import { e2eRequest } from './request';

/** Whether the target lets tests empty its database (only local and throwaway targets should). */
export async function resetAllowed(): Promise<boolean> {
  const health = await e2eRequest<{ ok: boolean; reset_allowed: boolean }>('GET', '');
  return health.reset_allowed;
}

/** Empties the target's database. */
export async function resetDatabase(): Promise<void> {
  await e2eRequest('POST', 'reset/');
}
