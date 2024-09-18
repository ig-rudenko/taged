#!/bin/sh
python manage.py makemigrations;
python manage.py migrate;
export DJANGO_COLLECT_STATIC=1
python manage.py collectstatic --no-input
export DJANGO_COLLECT_STATIC=0
gunicorn --workers 2 --bind 0.0.0.0:8000 taged.wsgi:application;
