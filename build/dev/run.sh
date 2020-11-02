#!/usr/bin/with-contenv bashio
cd /share
# todo this doesn't work but isnt' that bad
CONTAINER_ALREADY_STARTED="/home/cont_already_started_file"

if [ ! -e $CONTAINER_ALREADY_STARTED ]; then
    touch $CONTAINER_ALREADY_STARTED
    echo "First container startup--"
    echo "Run migration!"
    /home/remigrate.exp
fi

echo load fixtures!
python3 web/manage.py loaddata only_server.json

echo Starting http server!
# debug to check if the addon is reachable from the outside
#python3 -m http.server 8000

python3 web/manage.py runserver 0.0.0.0:8000