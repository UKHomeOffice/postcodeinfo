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


def root(*x):
    return os.path.join(PROJECT_ROOT, *x)

sys.path.insert(0, root('apps'))
sys.path.insert(1, root('lib'))

TESTING = 'test' in sys.argv

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY',
                            'kitqw3pp!@k&6$a(r4o_'
                            'm6deowtaeu35n4a%(k=ri0$*0vifbm')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Enable secure cookies in non-debug mode
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    'axes',

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
    'axes.middleware.FailedLoginMiddleware'
)

ROOT_URLCONF = 'postcodeinfo.urls'

WSGI_APPLICATION = 'postcodeinfo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'postcodeinfo'),
        'USER': os.environ.get('DB_USERNAME', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        # Empty for localhost through domain sockets
        # or '127.0.0.1' for localhost through TCP.
        'HOST': os.environ.get('DB_HOST', ''),
        # Set to empty string for default.
        'PORT': os.environ.get('DB_PORT', ''),
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
        'urlTokenAuthentication.UrlTokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}


##########################################################################
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

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d'
                '%(message)s')},

        'logstash': {
            '()': 'logstash_formatter.LogstashFormatterV1'}},

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'}},

    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG'}}}


if os.path.exists('/dev/log'):
    LOGGING['handlers']['syslog'] = {
        'level': 'DEBUG',
        'class': 'logging.handlers.SysLogHandler',
        'address': '/dev/log',
        'formatter': 'logstash'}
    LOGGING['loggers']['']['handlers'] = ['syslog']


if TESTING:
    LOGGING['loggers']['']['level'] = 'ERROR'


# AWS keys
AWS = {
    'region_name': os.environ.get('AWS_REGION_NAME', 'eu-west-1'),
    'access_key_id': os.environ.get('AWS_ACCESS_KEY_ID'),
    'secret_access_key': os.environ.get('AWS_SECRET_ACCESS_KEY'),
    's3_bucket_name': os.environ.get('S3_BUCKET_NAME')
}

# django-axes is used for locking out user/ipaddress combinations who have
# more than a certain number of failed logins
AXES_LOGIN_FAILURE_LIMIT=5
AXES_LOCK_OUT_AT_FAILURE=True
AXES_COOLOFF_TIME=1 # <- after 1 hour, they can try again
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP=True 

# .local.py overrides all the common settings.
try:
    from .local import *
except ImportError:
    pass
