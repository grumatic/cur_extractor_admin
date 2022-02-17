#!/bin/sh

python manage.py migrate --no-input
python manage.py collectstatic --no-input
python manage.py createsuperuser --no-input

# gunicorn cur_extractor.wsgi:application --bind 0.0.0.0:8000
uwsgi --socket :8000 --master --enable-threads --module cur_extractor.wsgi
