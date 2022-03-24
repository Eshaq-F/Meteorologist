#!/bin/sh

set -e

cmd=$1

if [ $cmd = 'web' ]; then
  python manage.py migrate
  exec python manage.py runserver 0.0.0.0:8000
fi
