#!/usr/bin/with-contenv bashio
cd /share/

CONTAINER_ALREADY_STARTED="/data/cont_already_started_file"
export PYTHONPATH=/share/web/act_assist:/share/:/share/web

if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    mkdir -p /data/
    touch $CONTAINER_ALREADY_STARTED
    python3 web/manage.py makemigrations
    python3 web/manage.py migrate --run-syncdb

    # TODO add the ability to load presets
    python3 web/manage.py loaddata /workspace/initial_server.json
fi

python3 web/manage.py runserver 0.0.0.0:8000
