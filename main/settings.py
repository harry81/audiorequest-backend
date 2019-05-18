"""
Django settings for main project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1h0&lx4!+=xw4r(n1v2q88zb!8a49l=v@u^ehi5eywzb+&^5hw'

# SECURITY WARNING: don't run with debu gturned on in production!
DEBUG = os.getenv("AWS_SESSION_TOKEN") == None

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'zappa_django_utils',
    'constance',

    'stt',
    'joonggonara',
    'dog'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

# CORS Config

CORS_ORIGIN_WHITELIST = (
    'www.hoodpub.com',
    'backend.hoodpub.com',
    '.serveo.net',
    'staging.hoodpub.com',
    'staging-backend.hoodpub.com',
    '.ap-northeast-2.amazonaws.com',
    '.hoodpub.com',
    'www.hoodpub.com.s3-website.ap-northeast-2.amazonaws.com',
    'localhost',
    'localhost:4200',
    '172.16.1.151:4200'
)

ALLOWED_HOSTS = CORS_ORIGIN_WHITELIST


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

WSGI_APPLICATION = 'main.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

dbname = "%sdb-stt" % ('staging-' if 'staging' in os.getenv('AWS_LAMBDA_LOG_GROUP_NAME', "") else "")

DATABASES = {
    'default': {
        'ENGINE': 'zappa_django_utils.db.backends.s3sqlite',
        'NAME': dbname,
        'BUCKET': 'hmapps-db'
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


sentry_sdk.init(
    dsn="https://bb4721469c9247419e17022763ee4b6d@sentry.io/1395534",
    integrations=[DjangoIntegration()]
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_STORAGE_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'hmapps')
AWS_AUDIO_STORAGE_BUCKET_NAME = 'hmapps-audio'
GS_BUCKET_NAME = os.getenv("GS_BUCKET_NAME")

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'LIMIT_ANONYMOUS': (60, 'Length of audio file for anonymous'),
    'LIMIT_USER': (60 * 5, 'Length of audio file for users'),
}

GAC_FILENAME = 'gac.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GAC_FILENAME
AUDIO_CONVERTER_PATH = 'bin/ffmpeg'
AUDIO_FFPROBE_PATH = 'bin/ffprobe'
AUDIO_EXT = ['wav', 'flac']
DEFAULT_EMAIL_ADDRESS = "chharry@gmail.com"
