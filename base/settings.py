import os
from pathlib import Path
from dotenv import dotenv_values

BASE_DIR = Path(__file__).resolve().parent.parent

config = dotenv_values(BASE_DIR / ".env")
SECRET_KEY = config.get("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = [config.get("ALLOWED_HOST")]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weather',
    'users',
    'django_celery_beat',
    'drf_spectacular',
]

AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'base.urls'

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
SPECTACULAR_SETTINGS = {
    'TITLE': 'Weather API',
    'DESCRIPTION': 'API documentation for Weather Reminder application',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

WSGI_APPLICATION = 'base.wsgi.application'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.get("POSTGRES_DB"),
        "USER": config.get("POSTGRES_USER"),
        "PASSWORD": config.get("POSTGRES_PASSWORD"),
        "HOST": config.get("POSTGRES_HOST"),
        "PORT": config.get("POSTGRES_PORT"),
    }
}
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
MEDIA_ROOT = BASE_DIR / "media_files"
MEDIA_URL = "/media_files/"
STATIC_ROOT = BASE_DIR / "static"

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'bazatinviktor@gmail.com'
EMAIL_HOST_PASSWORD = 'jlli ctxs boct jmwx'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = "weather:home"
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'

CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = config.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = config.get('CELERY_RESULT_BACKEND')
REDIS_HOST = config.get('REDIS_HOST')
REDIS_PORT = config.get('REDIS_PORT')

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
