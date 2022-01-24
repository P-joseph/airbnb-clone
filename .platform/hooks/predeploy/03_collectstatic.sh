#!/bin/bash

source /var/app/venv/*/bin/activate

python manage.py collectstatic --noinput