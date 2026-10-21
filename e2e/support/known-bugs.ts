/**
 * Known bug 13: the session page compares today's date in Berlin (the app's TIME_ZONE) with the UTC date of the
 * latest activity (views/public/session.py). While the two dates differ, from midnight Berlin time until midnight
 * UTC (one hour in winter, two in summer), the "<committee> is being debated right now!" banner is missing. Tests
 * of that banner expect to fail then.
 */
export function berlinAndUtcDatesDiffer(now = new Date()): boolean {
  const berlinDate = now.toLocaleDateString('sv-SE', { timeZone: 'Europe/Berlin' });
  return berlinDate !== now.toISOString().slice(0, 10);
}
