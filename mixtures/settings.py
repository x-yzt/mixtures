import os

import dj_database_url
from django_mistune.plugins import AddClasses, HeaderLevels


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'devKey'

DEBUG = True


# Hosts and URLs

ALLOWED_HOSTS = ('*',)

ROOT_HOSTCONF = 'mixtures.hosts'

ROOT_URLCONF = 'mixtures.urls'

DEFAULT_HOST = 'root'

PARENT_HOST = 'localhost'

HOST_PORT = '8000'


# Application definition

INSTALLED_APPS = [
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'django_hosts',
    'simple_history',
    'django_mistune',
    'drugcombinator.apps.DrugcombinatorConfig',
    'drugportals.apps.DrugportalsConfig',
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins' : [
                'django_hosts.templatetags.hosts_override',
            ]
        },
    },
]

WSGI_APPLICATION = 'mixtures.wsgi.application'


# Markdown preprocessor

MISTUNE_STYLES = {
    'default': {
        'plugins': [
            HeaderLevels(3),
            AddClasses({'ul': 'browser-default'}),
            # TODO: Target blank links
        ]
    },
}


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Email

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_SUBJECT_PREFIX = "[Mixtures system] "

DEFAULT_FROM_EMAIL = "system@mixtures.info"


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization

LANGUAGE_CODE = 'fr-fr'

LANGUAGES = (
    ('fr', 'Français'),
    ('en', 'English'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

LANGUAGE_COOKIE_NAME = 'language'


# Static files

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Production settings

if os.environ.get("PROD") == 'TRUE':

    print("Production settings found, overriding dev settings.")    
    
    DEBUG = False

    SECRET_KEY = os.environ["SECRET_KEY"]

    PARENT_HOST = os.getenv('PARENT_HOST', 'mixtures.info')

    ALLOWED_HOSTS = ['.' + PARENT_HOST]

    HOST_PORT = ''

    CSRF_COOKIE_DOMAIN = '.' + PARENT_HOST

    SESSION_COOKIE_DOMAIN = '.' + PARENT_HOST

    LANGUAGE_COOKIE_DOMAIN = '.' + PARENT_HOST

    DATABASES['default'] = dj_database_url.config(conn_max_age=600)

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'mixtures-app-cache'
        }
    }

    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    EMAIL_HOST = "mail.gandi.net"

    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASSWORD')

    EMAIL_HOST_USER = "system@mixtures.info"

    EMAIL_PORT = 465

    EMAIL_USE_SSL = True

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {'console': {'class': 'logging.StreamHandler'}},
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': os.getenv('DJANGO_LOG_LEVEL', 'ERROR')
            }
        }
    }

else:

    print("No production settings found, using dev settings.")
