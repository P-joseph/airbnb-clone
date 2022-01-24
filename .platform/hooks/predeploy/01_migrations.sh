#!/bin/bash

source /var/app/venv/*/bin/activate
cd /var/app/staging

python manage.py makemigrations
python manage.py migrate config
python manage.py migrate conversations
python manage.py migrate core
python manage.py migrate listsq
python manage.py migrate reservations
python manage.py migrate reviews
python manage.py migrate rooms
python manage.py migrate users
python manage.py dbshell
DROP INDEX documents_document_content_aa150741_like;
DROP INDEX documents_document_content_aa150741;
python manage.py createsuperuser
python manage.py seed_amenities
python manage.py seed_facilities
python manage.py seed_users --number 20
python manage.py seed_rooms --number 30