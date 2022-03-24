#!/bin/sh

set -e

cmd=$1

if [ $cmd = 'web' ]; then
  sleep 15
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver 0.0.0.0:8000
fi
