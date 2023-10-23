python manage.py makemigrations;
python manage.py migrate;
gunicorn --workers 2 --bind 0.0.0.0:8000 taged.wsgi:application;