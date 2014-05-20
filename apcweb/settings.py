﻿"""
Django settings for apcweb project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'inweb)8wu_)79+$f0z7)i6-lmc+u&o%p-cj-8xt5i*1rb!#954'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apc',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'apcweb.urls'

WSGI_APPLICATION = 'apcweb.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))

TEMPLATE_DIRS=(
    os.path.join(PROJECT_PATH,'templates'),
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
STATIC_ROOT = "/home/pi/projects/apcweb/static/"
#STATIC_ROOT = (
#    os.path.join(PROJECT_PATH,'static'),
#)
STATICFILES_FINDERS = (
'django.contrib.staticfiles.finders.AppDirectoriesFinder',
'django.contrib.staticfiles.finders.FileSystemFinder',
)
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
'django.core.context_processors.request',
)

STATIC_URL = '/static/'

LOGIN_URL = '/login'

#STATICFILES_DIRS = (
#    os.path.join(PROJECT_PATH,'static'),
#)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/apc_django_cache',
        'TIMEOUT': 99999999999999999,
    }
}