"""
Django settings for postcodeinfo project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
PROJECT_ROOT = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(PROJECT_ROOT)
root = lambda *x: os.path.join(PROJECT_ROOT, *x)

sys.path.insert(0, root('apps'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
    'kitqw3pp!@k&6$a(r4o_m6deowtaeu35n4a%(k=ri0$*0vifbm')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_gis',

    'postcode_api'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'postcodeinfo.urls'

WSGI_APPLICATION = 'postcodeinfo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DJANGO_DB_NAME', 'postcodeinfo'),
        'USER': os.environ.get('DJANGO_DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', ''),
        'HOST': os.environ.get('DJANGO_DB_HOST', ''),                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': os.environ.get('DJANGO_DB_PORT', ''),                      # Set to empty string for default.
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'Europe/London'

USE_I18N = False

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_ROOT = root('static')

STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

#################################################################################
# fix for 'relation "auth_user" does not exist' when running tests on Django 1.8
# see https://github.com/evonove/django-oauth-toolkit/issues/204

# makemigrations requires this for some reason or it errors
# Just set to the default value
# OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'

# # tell django where to put the oauth2 migrations
# MIGRATION_MODULES = {
#    # key: app name, value: a fully qualified package name, not the usual `app_label.something_else`
#   'oauth2_provider': 'postcode_api.migrations.oauth2_provider',
# }


################################################################################
# Sentry integration for error notifications
# from https://sentry.service.dsd.io/docs/platforms/django/

RAVEN_CONFIG = {
    'dsn': os.environ.get('SENTRY_DSN', '')
}

# Add raven to the list of installed apps
INSTALLED_APPS = INSTALLED_APPS + (
    # ...
    'raven.contrib.django.raven_compat',
)

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass
