#!/bin/bash
DJANGO_USER="root"
DJANGO_PROJECT="activity_assistant"
CONTAINER_ALREADY_STARTED="/data/cont_already_started_file"

cd /opt/$DJANGO_PROJECT/web
export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT
export DJANGO_SETTINGS_MODULE=settings


if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    echo $PWD
    python3 manage.py migrate
    python3 manage.py loaddata /home/minimal.json
fi


# Start Gunicorn processes
exec gunicorn act_assist.wsgi:application --bind 0.0.0.0:8000