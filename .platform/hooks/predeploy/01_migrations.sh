#!/bin/bash

source /var/app/venv/*/bin/activate
cd /var/app/staging

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py showmigrations
winpty python3 manage.py createsuperuser
python3 manage.py seed_amenities
python3 manage.py seed_facilities
python3 manage.py seed_users --number 20
python3 manage.py seed_rooms --number 30