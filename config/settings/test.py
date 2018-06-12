from os import environ
from .base import *

THIRD_PARTY_APPS = (
    'django_nose',  # for unittest using this package
)

INSTALLED_APPS += THIRD_PARTY_APPS

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        # The following settings are not used with sqlite3:
        'USER': environ.get('LAZACOM3PL_TEST_USER', 'postgresuser'),
        'PASSWORD': environ.get('LAZACOM3PL_TEST_PASSWORD', 'mysecretpass'),
        'HOST': environ.get('LAZACOM3PL_TEST_HOST', 'postgres'),  # Empty for localhost through domain sockets
                               # or '127.0.0.1' for localhost through TCP.
        'PORT': environ.get('LAZACOM3PL_TEST_PORT', '5432'),  # Set to empty string for default.

        'ATOMIC_REQUESTS': True,
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Use nose to run all tests
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

CELERY_ALWAYS_EAGER = True
PYREBASE_MOCK = True
BROKER_BACKEND='memory'
CELERY_EAGER_PROPAGATES_EXCEPTIONS=True
