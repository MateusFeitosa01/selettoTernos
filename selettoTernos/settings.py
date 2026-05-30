"""
Django settings for selettoTernos project.
"""

import os
from pathlib import Path
from decouple import config
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# SEGURANÇA
# =========================================================

SECRET_KEY = config(
    'DJANGO_SECRET_KEY',
    default='django-insecure-dev-key-change-in-production'
)

DEBUG = config(
    'DJANGO_DEBUG',
    default=False,
    cast=bool
)

ALLOWED_HOSTS = config(
    'DJANGO_ALLOWED_HOSTS',
    default='127.0.0.1,localhost,seletto-ternos.onrender.com'
).split(',')


# =========================================================
# APPS
# =========================================================

INSTALLED_APPS = [
    'daphne',
    'axes',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
    'django_htmx',
    'rest_framework',

    'core',
    'accounts',
    'filas',
    'atendimentos',
    'paineis',
]


# =========================================================
# MIDDLEWARE
# =========================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # proteção login brute force
    'axes.middleware.AxesMiddleware',

    # static files produção
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'django_htmx.middleware.HtmxMiddleware',
]


# =========================================================
# URLS / TEMPLATES
# =========================================================

ROOT_URLCONF = 'selettoTernos.urls'

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


# =========================================================
# ASGI / WSGI
# =========================================================

WSGI_APPLICATION = 'selettoTernos.wsgi.application'

ASGI_APPLICATION = 'selettoTernos.asgi.application'


# =========================================================
# DATABASE
# =========================================================

DATABASES = {
    'default': dj_database_url.config(
        default=config(
            'DATABASE_URL',
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
        ),
        conn_max_age=0,
        ssl_require=True
    )
}


# =========================================================
# PASSWORD VALIDATION
# =========================================================

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


# =========================================================
# INTERNACIONALIZAÇÃO
# =========================================================

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Recife'

USE_I18N = True

USE_TZ = True


# =========================================================
# STATIC FILES
# =========================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_STORAGE = (
    'whitenoise.storage.CompressedManifestStaticFilesStorage'
)


# =========================================================
# DEFAULT PK
# =========================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =========================================================
# AUTH
# =========================================================

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = '/accounts/login/'

LOGIN_REDIRECT_URL = '/adminSeletto/'

LOGOUT_REDIRECT_URL = '/'


# =========================================================
# DJANGO AXES
# =========================================================

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5

AXES_COOLOFF_TIME = 1

AXES_RESET_ON_SUCCESS = True


# =========================================================
# CHANNELS / REDIS
# =========================================================

REDIS_URL = config('REDIS_URL', default=None)

if REDIS_URL:

    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }

else:

    # fallback local/dev
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }


# =========================================================
# HTTPS / PRODUÇÃO
# =========================================================

CSRF_TRUSTED_ORIGINS = [
    "https://*.onrender.com",
]

SECURE_PROXY_SSL_HEADER = (
    'HTTP_X_FORWARDED_PROTO',
    'https'
)

SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG

SECURE_SSL_REDIRECT = not DEBUG

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'


# =========================================================
# LOGGING
# =========================================================

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },

    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}