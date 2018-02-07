"""
Django production settings for eypstats project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import raven
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'test_#^^3rh08z(1eun9czpb^0-5c%t$!^!fl8ie5-gfa2^i%gwpjtm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['stats.eyp.org', 'ga-statistics.herokuapp.com']

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
    'statistics',
    'imagekit',
    'raven.contrib.django.raven_compat',
    'django_s3_storage'
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
                'statistics.context_processors.analytics',
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
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
}

db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# Media file settings

# The AWS region to connect to.
AWS_REGION = "eu-west-2"

# The AWS access key to use.
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']

# The AWS secret access key to use.
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

# The name of the bucket to store files in.
AWS_S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"


# GOOGLE_ANALYTICS = "UA-73435932-1"
GOOGLE_ANALYTICS = ""

RAVEN_CONFIG = {
    'dsn': 'https://e1293cf510704122a3ee1c9a35477c7a:eeabde9a71f54a3a898295146aab5520@sentry.io/156485',
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': '15098a2e0423b7149fad67f1294fa182aea08fbf',
}
