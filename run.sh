python ./taged_web/elasticsearch_control.py;
python manage.py makemigrations;
python manage.py migrate;
python manage.py collectstatic --noinput --settings=taged_web.static_settings;
python manage.py runserver 0.0.0.0:8000;