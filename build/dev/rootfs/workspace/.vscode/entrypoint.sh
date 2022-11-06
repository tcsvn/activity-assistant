#!/bin/bash
cd /share/


# Define env variables and dump them into env.sh (needed since ssh vscode uses no login shell)
export WORKSPACE_FOLDER=/workspace
#the hass api act /web/assist since settings.py should be accessable
export PYTHONPATH=${WORKSPACE_FOLDER}:/share/hass_api:/share/web/act_assist:/share/:/share/web
declare -xp > env.sh

CONTAINER_ALREADY_STARTED="/data/cont_already_started_file"

if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    mkdir -p /data/
    touch $CONTAINER_ALREADY_STARTED
    python3 web/manage.py makemigrations
    python3 web/manage.py migrate --run-syncdb

    # TODO add the ability to load presets
    python3 web/manage.py loaddata /workspace/initial_server.json
fi

# Hand off to the CMD
exec "$@"