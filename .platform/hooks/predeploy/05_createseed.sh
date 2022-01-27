#!/bin/bash

source /var/app/venv/*/bin/activate
cd /var/app/staging

python3 manage.py seed_amenities
python3 manage.py seed_facilities
python3 manage.py seed_users --number 20
python3 manage.py seed_rooms --number 40
python3 manage.py seed_reviews --number 100