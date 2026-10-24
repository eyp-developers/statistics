"""
Django production settings for eypstats project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from pathlib import Path

import dj_database_url
import sentry_sdk

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
IS_DEVELOPMENT = False

ALLOWED_HOSTS = ['stats.eyp.org', 'ga-statistics.herokuapp.com', 'ga-statistics-staging.herokuapp.com']
SECURE_SSL_REDIRECT = True

CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'statisticscore',
    'django_rename_app',
    'imagekit',
    'django_tables2',
    'django_filters',
    'bootstrap3'
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

ROOT_URLCONF = 'eypstats.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'eypstats.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Starting with Django 3.2 it is possible to alter the automatically generated primary key field type
# We want to keep the pre-3.2 default behaviour which is to set implicit primary key fields to be of the type
# AutoField, which is internally represented as an Integer
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "bucket_name": os.environ['DEFAULT_STORAGE_BUCKET_NAME'],
            "access_key": os.environ['DEFAULT_STORAGE_ACCESS_KEY_ID'],
            "secret_key": os.environ['DEFAULT_STORAGE_SECRET_ACCESS_KEY'],
            "region_name": os.environ['DEFAULT_STORAGE_REGION'],
            "endpoint_url": os.environ['DEFAULT_STORAGE_ENDPOINT_URL'],
        },
    },
}


# Initialise sentry sdk, send to self-hosted bugsink
sentry_sdk.init(
    dsn=os.environ['BUGSINK_DSN'],
    send_default_pii=True,
    traces_sample_rate=0,
    # Check https://docs.sentry.io/platforms/python/data-management/data-collected/ to configure what data is collected
    data_collection={
        "user_info": True,
    },
)
