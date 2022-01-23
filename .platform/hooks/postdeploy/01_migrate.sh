#!/bin/bash

source "$PYTHONPATH/activate" && {
# log which migrations have already been applied
python manage.py showmigrations;
# migrate
python manage.py migrate --noinput;
}