from os import getenv

import dj_database_url

from mixtures.settings import *


# General settings

DEBUG = False

SECRET_KEY = getenv("SECRET_KEY")


# Hosts

PARENT_HOST = getenv('PARENT_HOST', 'mixtures.info')

HOST_PORT = ''

ALLOWED_HOSTS = ['.' + PARENT_HOST]

CSRF_COOKIE_DOMAIN = '.' + PARENT_HOST

SESSION_COOKIE_DOMAIN = '.' + PARENT_HOST

LANGUAGE_COOKIE_DOMAIN = '.' + PARENT_HOST

CSRF_TRUSTED_ORIGINS = [
    'https://' + PARENT_HOST,
    'https://*.' + PARENT_HOST,
]


# Database

DATABASES['default'] = dj_database_url.config(conn_max_age=600)


# Cache

CACHES['default'] = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'mixtures-app-cache'
}


# Email

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = "mail.gandi.net"

EMAIL_HOST_PASSWORD = getenv('EMAIL_PASSWORD')

EMAIL_HOST_USER = "system@mixtures.info"

EMAIL_PORT = 465

EMAIL_USE_SSL = True


# Logs

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': getenv('DJANGO_LOG_LEVEL', 'ERROR')
        }
    }
}
