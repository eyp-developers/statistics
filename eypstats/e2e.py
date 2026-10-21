"""
Settings for running the app under the Playwright suite in /e2e (see e2e/README.md).

Uses SQLite in e2e/.data unless DATABASE_URL is set (e.g. Postgres in CI).
"""
import os

from eypstats.settings import *  # noqa: F401,F403
from eypstats.settings import BASE_DIR, DATABASES

E2E_DATA_DIR = os.path.join(BASE_DIR, 'e2e', '.data')

# Never report test runs to the production Sentry project.
RAVEN_CONFIG = {'dsn': None}

E2E_ENDPOINTS_ENABLED = True
E2E_TOKEN = os.environ.get('E2E_TOKEN', 'local-e2e-token')

if not os.environ.get('DATABASE_URL'):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(E2E_DATA_DIR, 'e2e.sqlite3'),
        # SQLite allows one writer at a time; wait for the lock instead of failing when workers write in parallel.
        'OPTIONS': {'timeout': 20},
    }

# Uploaded session pictures are served by Django itself while IS_DEVELOPMENT is on (inherited as True).
MEDIA_ROOT = os.path.join(E2E_DATA_DIR, 'media')
