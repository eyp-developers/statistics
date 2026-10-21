import { e2eRequest } from './request';

export type StatisticsMode = 'S' | 'C' | 'JF' | 'SF' | 'R' | 'RC';

export interface SessionInput {
  name: string;
  description?: string;
  mode?: StatisticsMode;
  type?: 'IS' | 'IF' | 'NS' | 'RS' | 'SS' | 'OE';
  country?: string;
  email?: string;
  /** YYYY-MM-DD */
  start_date?: string;
  end_date?: string;
  visible?: boolean;
  voting_enabled?: boolean;
  gender_enabled?: boolean;
  technical_problems?: boolean;
  max_rounds?: number;
  admin_password?: string;
  submission_password?: string;
  committees?: { name: string; topic?: string; subtopics?: string[] }[];
  /** Committee name */
  active_debate?: string;
  active_round?: number;
}

export interface Account {
  username: string;
  password: string;
}

export interface CreatedSession {
  id: number;
  name: string;
  admin: Account;
  submission: Account;
  committees: { id: number; name: string; subtopics: { id: number; text: string }[] }[];
}

export interface SessionState {
  active_debate?: string;
  active_round?: number;
  visible?: boolean;
  technical_problems?: boolean;
  voting_enabled?: boolean;
  gender_enabled?: boolean;
}

/**
 * A session name no other test, or earlier run against a shared target, will use. The app derives the login
 * usernames from the name, so names must differ by more than spacing or case.
 */
export function uniqueSessionName(prefix = 'E2E'): string {
  return `${prefix} ${crypto.randomUUID().slice(0, 8)}`;
}

export function createSession(input: SessionInput): Promise<CreatedSession> {
  return e2eRequest('POST', 'sessions/', input);
}

export function setSessionState(sessionId: number, state: SessionState): Promise<Required<SessionState>> {
  return e2eRequest('POST', `sessions/${sessionId}/state/`, state);
}

/** Committees and subtopics are named; debate and round default to the session's active ones. */
export interface SessionData {
  points?: {
    committee: string;
    debate?: string;
    round?: number;
    type?: 'P' | 'DR';
    /** Subtopics of the debated committee; defaults to ["General"] */
    subtopics?: string[];
    minutes_ago?: number;
  }[];
  content?: { committee: string; text: string; debate?: string; type?: 'P' | 'DR'; minutes_ago?: number }[];
  votes?: {
    committee: string;
    debate?: string;
    in_favour?: number;
    against?: number;
    abstentions?: number;
    absent?: number;
    minutes_ago?: number;
  }[];
  genders?: { committee: string; gender: 'F' | 'M' | 'O'; minutes_ago?: number }[];
}

/** Adds points, content points, votes and gender entries in bulk. Returns the created IDs. */
export function addSessionData(
  sessionId: number,
  data: SessionData,
): Promise<{ points: number[]; content: number[]; votes: number[]; genders: number[] }> {
  return e2eRequest('POST', `sessions/${sessionId}/data/`, data);
}

/** Deletes the session, its two accounts and all its data. Fine to call for a session that's already gone. */
export async function deleteSession(sessionId: number): Promise<void> {
  await e2eRequest('DELETE', `sessions/${sessionId}/`);
}
