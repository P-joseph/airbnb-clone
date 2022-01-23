##!/bin/bash
#
#source /var/app/venv/*/bin/activate
#cd /var/app/staging
#
#python manage.py collectstatic --noinput
#python manage.py seed_amenities
#python manage.py seed_facilities
#python manage.py seed_users --number 20
#python manage.py seed_rooms --number 30
#python manage.py createsuperuser
#python manage.py migrate --run --syncdb
#python manage.py makemigrations user
#python manage.py makemigrations web
#python manage.py makemigrations
#python manage.py migrate
#django-admin.py migrate

#!/bin/bash

source "$PYTHONPATH/activate" && {
# log which migrations have already been applied
python manage.py showmigrations;
# migrate
python manage.py migrate --noinput;
}