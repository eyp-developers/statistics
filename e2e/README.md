# End-to-end tests

Playwright tests (TypeScript) for EYP Statistics. They talk to the app only over HTTP, so they run against a local
server, CI or any deployed preview that has the test data endpoints switched on.

## Running locally

One-time setup, from the repository root:

```bash
uv venv --python 3.11.9 .venv && uv pip install --python .venv/bin/python -r requirements.txt
cd e2e && npm install && npx playwright install chromium
```

Then, from `e2e/`:

```bash
npm test                      # starts a local server on SQLite with a fresh database, runs everything
npx playwright test --workers=8
npm run test:ui               # Playwright UI mode
npx playwright test --repeat-each=3 --workers=8   # stability check
```

With no `E2E_BASE_URL`, Playwright runs `start-server.sh`. It recreates the database, migrates, collects static files
and starts gunicorn on port 8765 with `eypstats.e2e` settings. SQLite is the default. Set `DATABASE_URL` to use
Postgres instead (the database is flushed on start).

## Running against another server

```bash
E2E_BASE_URL=https://preview.example.com E2E_TOKEN=... npm test
```

This also works for a local server you keep running between runs, which is handy while writing tests:

```bash
e2e/start-server.sh                                    # from the repository root, in one terminal
E2E_BASE_URL=http://127.0.0.1:8765 npx playwright test # in e2e/
```

The target must run with `E2E_ENDPOINTS_ENABLED=true` and the same `E2E_TOKEN`. Tests only touch the sessions they
create and delete them afterwards, so any number of runs can share one server. Set `E2E_KEEP_DATA=1` to keep the
sessions for debugging.

| Variable | Default | Meaning |
| --- | --- | --- |
| `E2E_BASE_URL` | unset (start local server) | App to test |
| `E2E_TOKEN` | `local-e2e-token` | Sent as `X-E2E-Token`; must match the server |
| `E2E_PORT` | `8765` | Port for the local server |
| `E2E_KEEP_DATA` | unset | `1` keeps created sessions |
| `DATABASE_URL` | unset (SQLite) | Database for the local server |

## Layout

Tests are grouped by domain, not priority.

```
tests/<domain>/*.spec.ts   e.g. tests/sessions/create-session.spec.ts
support/e2e-api/           plain functions calling /__e2e__/: sessions.ts, login.ts
support/fixtures.ts        test + expect with createSession and cleanUpSession
support/                   env, small UI helpers (datepicker.ts, home-page.ts), known-bugs.ts
assets/                    files tests upload
```

- Import `test` and `expect` from `support/fixtures`. The `createSession` fixture creates a session through the
  endpoints and deletes it after the test; `cleanUpSession(id)` does the same for sessions made through the UI.
- The functions in `support/e2e-api/` (`createSession`, `addSessionData`, `setSessionState`, `loginAs`, ...) are
  plain `fetch` calls and can be used directly.
- Set up data through the endpoints, not the UI, unless the UI flow is what the test is about.
- Give every session a unique name (`uniqueSessionName()`). Never assume anything about data the test didn't
  create: other tests run against the same server at the same time. Check properties of your own data instead
  (e.g. "my sessions are listed newest first", not "page 1 shows exactly these 12"). `findSessionCard()` walks the
  home page's pages to find a session.
- Known bugs are pinned with `test.fail` and a comment naming the bug, so they start reporting once fixed.
- Locate things the way a user finds them: `getByRole`, `getByLabel`, `getByText`. When the page's markup makes
  that impossible, fix the markup (add a label, close a tag, add an accessible name) rather than reaching for CSS
  selectors. No page objects for now; a small helper function in the spec file is enough.

## Test data endpoints (`/__e2e__/`)

Defined in `statisticscore/e2e/`. Every endpoint answers 404 unless `E2E_ENDPOINTS_ENABLED` is true and the request
carries a matching `X-E2E-Token` header. Requests and responses are JSON. A rewritten backend has to keep this
contract.

### `POST /__e2e__/sessions/` → 201

Every field but `name` is optional.

```json
{
  "name": "E2E 3k9x2a",
  "description": "E2E test session",
  "mode": "JF",
  "type": "RS",
  "country": "DE",
  "email": "e2e@example.com",
  "start_date": "2026-10-21",
  "end_date": "2026-10-28",
  "visible": false,
  "voting_enabled": true,
  "gender_enabled": false,
  "technical_problems": false,
  "max_rounds": 3,
  "admin_password": "e2e-admin-password",
  "submission_password": "e2e-submission-password",
  "committees": [{ "name": "ENVI", "topic": "Climate", "subtopics": ["Emissions"] }],
  "active_debate": "ENVI",
  "active_round": 1
}
```

Every committee gets a "General" subtopic first. Response:

```json
{
  "id": 12,
  "name": "E2E 3k9x2a",
  "admin": { "username": "e2e3k9x2a_admin", "password": "e2e-admin-password" },
  "submission": { "username": "e2e3k9x2a", "password": "e2e-submission-password" },
  "committees": [{ "id": 40, "name": "ENVI", "subtopics": [{ "id": 90, "text": "General" }, { "id": 91, "text": "Emissions" }] }]
}
```

409 if the name, or the usernames derived from it, are taken.

### `POST /__e2e__/sessions/<id>/state/` → 200

Any of `active_debate` (committee name), `active_round`, `visible`, `technical_problems`, `voting_enabled`,
`gender_enabled`. Returns all six.

### `POST /__e2e__/sessions/<id>/data/` → 201

Adds data in bulk. Committees and subtopics are given by name; `debate` defaults to the active debate and `round` to
the active round. `minutes_ago` backdates an entry. Every list is optional.

```json
{
  "points": [{ "committee": "AFCO", "type": "P", "subtopics": ["Emissions"], "round": 1, "debate": "ENVI" }],
  "content": [{ "committee": "AFCO", "text": "We should act now", "type": "DR" }],
  "votes": [{ "committee": "AFCO", "in_favour": 10, "against": 3, "abstentions": 1, "absent": 0 }],
  "genders": [{ "committee": "ENVI", "gender": "F", "minutes_ago": 30 }]
}
```

Returns the created IDs: `{"points": [1], "content": [1], "votes": [1], "genders": [1]}`.

### `DELETE /__e2e__/sessions/<id>/` → 204

Deletes the session, both its accounts and all its data. Also 204 if it's already gone.

### `POST /__e2e__/login/` → 200

`{"session_id": 12, "role": "admin" | "submission"}` or `{"username": "..."}`. Logs the caller in (sets the session
cookie) and returns `{"username": "..."}`.
