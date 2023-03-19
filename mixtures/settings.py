from pathlib import Path

from django_mistune.plugins import AddClasses, HeaderLevels, TargetBlankLinks


# General settings

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = True

SECRET_KEY = 'devkey'


# Hosts and URLs

ROOT_HOSTCONF = 'mixtures.hosts'

ROOT_URLCONF = 'mixtures.urls'

DEFAULT_HOST = 'root'

PARENT_HOST = 'localhost'

HOST_PORT = '8000'

ALLOWED_HOSTS = [
    f'.{PARENT_HOST}',
    f'.{PARENT_HOST}:{HOST_PORT}',
]


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
    'huey.contrib.djhuey',
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
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'django_hosts.templatetags.hosts_override',
            ]
        },
    },
]

FORM_RENDERER = "django.forms.renderers.DjangoDivFormRenderer"

WSGI_APPLICATION = 'mixtures.wsgi.application'


# Huey task scheduler

HUEY = {
    'name': "mixtures",
    'huey_class': 'huey.SqliteHuey',
    'filename': './huey.sqlite',
    'immediate': False,
    'consumer': {
        'periodic': False,  # Disable crontab feature
    },
}


# Markdown preprocessor

MISTUNE_STYLES = {
    'default': {
        'plugins': [
            HeaderLevels(top=4),
            AddClasses({
                'ul': 'browser-default',
                'img': ('responsive-img', 'materialboxed'),
            }),
            TargetBlankLinks(),
        ]
    },
}


# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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
    BASE_DIR / 'locale',
)

LANGUAGE_COOKIE_NAME = 'language'


# Static files

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Cache

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}


# Other credentials

ARCHIVE_ACCESS = 'L9DohDZqKr2r6Oty'

ARCHIVE_SECRET = ''
