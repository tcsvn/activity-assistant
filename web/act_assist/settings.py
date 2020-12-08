"""
Django settings for hassbrain_web project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import logging
logger = logging.getLogger(__name__)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#ALLOWED_HOSTS = ['0.0.0.0', 'localhost']

# allow hosts for the home net
#ALLOWED_HOSTS += ['192.168.178.{}'.format(j) for j in range(256)]
ALLOWED_HOSTS = ['*'] # TODO debug measure 

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', 'rest_framework', 'qr_code',
    'rest_framework.authtoken',
    'frontend.apps.FrontendConfig',
    'backend.apps.BackendConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'act_assist.urls'

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

WSGI_APPLICATION = 'act_assist.wsgi.application'



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

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_URL = '/static/'

SERVE_MEDIA = True
MEDIA_URL = '/media/'
HASS_API_URL = 'http://supervisor/core/api'

DATA_ROOT = '/data/'
MEDIA_ROOT = DATA_ROOT + 'media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_ROOT + 'db.sqlite3',
    }
}

# experiment
POLL_INTERVAL_LST = ['5s', '1m', '10m', '30m', '2h', '6h']
DATASET_PATH = DATA_ROOT + 'datasets/' # path where all the datasets lie
ACTIVITY_FILE_NAME="activities_subject_%s.csv"
DATA_FILE_NAME='devices.csv'
DATA_MAPPING_FILE_NAME='device_mapping.csv'
PRIOR_ACTIVITY_FILE_NAME = "prior_activities_subject_%s.csv"
DEV_ROOM_ASSIGNMENT_FILE_NAME = "devices_and_areas.csv"
ACT_ROOM_ASSIGNMENT_FILE_NAME = "activities_and_areas.csv"

DB_URL = 'sqlite:////config/home-assistant_v2.db' 

ACT_ASSIST_VERSION = "v0.0.1-alpha"
ACT_ASSIST_RELEASE_LINK = "https://github.com/tcsvn/activity-assistant-logger/releases/download/{}/activity-assistant.apk".format(ACT_ASSIST_VERSION)

# API URLS
URL_SERVER = r'server'
URL_DEVICE_PREDICTIONS = r'devicepredictions'
URL_ACTIVITY_PREDICTIONS = r'activitypredictions'
URL_PERSONS = r'/person/'
URL_SYNTHETIC_ACTIVITY = r'syntheticactivity'
URL_DEVICE_COMPONENT = r'devcomp'

# qrcode cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'qr-code': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'qr-code-cache',
        'TIMEOUT': 3600
    }
}

QR_CODE_CACHE_ALIAS = 'qr-code'


from os import environ
ENV_SETTINGS = environ.get('DJANGO_ENV') or 'development'
if ENV_SETTINGS == 'development':
    try:
        from act_assist.local_settings.development import *
    except ImportError:
        logger.error('couldn\'t import development settings')
        raise

elif ENV_SETTINGS == 'production':
    try:
        from act_assist.local_settings.production import *
    except ImportError:
        logger.error('couldn\'t import development settings')
        raise 
