#!/bin/bash

source /var/app/venv/*/bin/activate
cd /var/app/staging

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py seed_amenities
python manage.py seed_facilities
python manage.py seed_users --number 20
python manage.py seed_rooms --number 30