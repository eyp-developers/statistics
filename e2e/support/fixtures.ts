import { test as base, expect } from '@playwright/test';
import { createSession, deleteSession, uniqueSessionName, type CreatedSession, type SessionInput } from './e2e-api/sessions';
import { env } from './env';

type Fixtures = {
  /** Creates a session through the test data endpoints (with a unique name unless given) and deletes it afterwards. */
  createSession: (input?: Partial<SessionInput>) => Promise<CreatedSession>;
  /** Deletes a session the test created another way (e.g. through the create form) once the test is done. */
  cleanUpSession: (sessionId: number) => void;
  sessionIdsToDelete: number[];
};

export const test = base.extend<Fixtures>({
  sessionIdsToDelete: async ({}, use) => {
    const ids: number[] = [];
    await use(ids);
    // E2E_KEEP_DATA=1 keeps what the test created, for debugging.
    if (!env.keepData) {
      for (const id of ids) {
        await deleteSession(id);
      }
    }
  },

  createSession: async ({ sessionIdsToDelete }, use) => {
    await use(async (input = {}) => {
      const session = await createSession({ name: uniqueSessionName(), ...input });
      sessionIdsToDelete.push(session.id);
      return session;
    });
  },

  cleanUpSession: async ({ sessionIdsToDelete }, use) => {
    await use((sessionId) => sessionIdsToDelete.push(sessionId));
  },
});

export { expect };
