import os
import django_heroku


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
    'markdown_deux',
    'drugcombinator.apps.DrugcombinatorConfig',
    'drugportals.apps.DrugportalsConfig',
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
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

MARKDOWN_DEUX_STYLES = {
    'default': {
        'extras': {
            'code-friendly': None,
            'cuddled-lists': None,
            'demote-headers': 3,
            'html-classes': {'ul': 'browser-default'},
            'target-blank-links': None
        },
        'safe_mode': 'escape'
    }
}


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


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

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
    os.path.join(BASE_DIR, "locale_overrides"),
)

LANGUAGE_COOKIE_NAME = 'language'


# Static files

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Production settings

if os.environ.get("PROD") == 'TRUE':

    print("Production settings found, overriding dev settings.")    
    
    django_heroku.settings(locals(), logging=False, allowed_hosts=False)

    DEBUG = False

    ALLOWED_HOSTS = ['.mixtures.info']

    PARENT_HOST = 'mixtures.info'

    HOST_PORT = ''

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'mixtures-app-cache'
        }
    }

    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

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
