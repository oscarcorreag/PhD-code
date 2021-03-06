"""
Django settings for ridesharing_django project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import sys

# sys.path.append("C:\\Users\\oscarcg\\Dropbox\\Education\\Unimelb PhD\\code\\common")
# sys.path.append("C:\\Users\\oscarcg\\Dropbox\\Education\\Unimelb PhD\\code\\VST-RS")
# sys.path.append("C:\\Users\\oscarcg\\Dropbox\\Education\\Unimelb PhD\\code\\Hotspot-based")
# sys.path.append("C:\\Users\\oscarcg\\Dropbox\\Education\\Unimelb PhD\\code\\Traffic")

sys.path.append("../common")
sys.path.append("../VST-RS")
sys.path.append("../Hotspot-based")
sys.path.append("../Traffic")

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '53lb8h!9!8-7$ft^u_iwda=&l$-gd&&tn&0lm741%r1l))-w@)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '4000L-122353-W', '10.13.196.38', '192.168.1.5', '10.13.206.51']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hotspots',
    'congestion',
    'rs',
    'csdp',
    'rest_framework',
    # 'django_celery_results',
    'djcelery',
    'push_notifications',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ridesharing_django.urls'

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

WSGI_APPLICATION = 'ridesharing_django.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'osm',
        'USER': 'postgres',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
    },
}

REST_FRAMEWORK = {
    'EXCEPTION_HANDLER': 'rs.exceptions.custom_exception_handler'
}

CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
# CELERY_CACHE_BACKEND = 'djcelery.backends.cache:CacheBackend'

PUSH_NOTIFICATIONS_SETTINGS = {
    "UPDATE_ON_DUPLICATE_REG_ID": True,
    "FCM_API_KEY": "AAAAMdzJBt0:APA91bH3SFuZ02FRI2LbSGQigqLdYV8kHbaZl7YTkW-QijJnL2zD806IeyiGzehkhSaY9ZTC80HsD3wkNH-AYM6T0KuJuVyKN5r5K0FwKRFGFLN5gjS3dXdnpgRh0UQ0_tOI5UQLHmp8",
    # "FCM_POST_URL": "https://fcm.googleapis.com/v1/projects/abrs-unimelb/messages:send HTTP/1.1"
}