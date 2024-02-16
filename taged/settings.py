"""
Django settings for taged project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import logging
import os
import time
import uuid
from pathlib import Path

from elasticsearch import Elasticsearch
from requests.exceptions import ConnectionError as ElasticConnectionError

from elasticsearch_control import IndexRegister
from elasticsearch_control.transport import elasticsearch_connector
from taged_web.es_index import PostIndex

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-o$84xxrt-ip(b7&)wy)ka(@s@7tq()0vs0u(hu*mo7-^uvc_54",
)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "ckeditor",
    "ckeditor_uploader",
    "rest_framework",
    "taged_web.apps.TagedWebConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "taged.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_USER_MODEL = "taged_web.User"
WSGI_APPLICATION = "taged.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"

if os.getenv("DJANGO_COLLECT_STATIC", "0") == "1":
    STATIC_ROOT = BASE_DIR / "static"
else:
    STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


DATA_UPLOAD_MAX_MEMORY_SIZE = 300_000_000  # 100МБ

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}


def get_filename(file_name: str, request) -> str:
    return str(uuid.uuid4()) + "-" + file_name


CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_USER = True
CKEDITOR_FILENAME_GENERATOR = "taged.settings.get_filename"
CKEDITOR_UPLOAD_PATH = "notes/"

logging.basicConfig(filename="logs", level=logging.INFO)

# В формате `es01:9200,es02:9201,es03:9202`
ELASTICSEARCH_HOSTS_raw_str = os.getenv("ELASTICSEARCH_HOSTS")

if ELASTICSEARCH_HOSTS_raw_str:

    ELASTICSEARCH_HOSTS = [
        {"host": host.split(":")[0], "port": int(host.split(":")[1])}
        for host in ELASTICSEARCH_HOSTS_raw_str.split(",")
    ]
    ELASTICSEARCH_TIMEOUT = 10

    print("ELASTICSEARCH_HOSTS:", ELASTICSEARCH_HOSTS)

    # Инициализируем подключение к Elasticsearch
    elasticsearch_connector.init(
        es=Elasticsearch(ELASTICSEARCH_HOSTS), timeout=ELASTICSEARCH_TIMEOUT
    )

    # Регистратор индексов в Elasticsearch
    es_index_register = IndexRegister()

    while True:
        try:
            # Создаем индексы
            es_index_register.register_index(PostIndex)
            print("Registered PostIndex")
            break
        except ElasticConnectionError as error:
            print(error)
            # Если Elasticsearch недоступен, то пытаемся еще раз
            time.sleep(10)
