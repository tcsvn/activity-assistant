#!/usr/bin/env bashio

DJANGO_USER="root"
DJANGO_PROJECT="activity_assistant"
CONTAINER_ALREADY_STARTED="/data/cont_already_started_file"

cd /opt/$DJANGO_PROJECT/web
export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT
export DJANGO_SETTINGS_MODULE=settings


if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    mkdir -p /data/
    touch $CONTAINER_ALREADY_STARTED
    python3 manage.py makemigrations
    python3 manage.py migrate --run-syncdb
    python3 manage.py loaddata /home/initial_server.json
fi

# Hand off to the CMD
exec "$@"
