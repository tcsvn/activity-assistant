#!/usr/bin/with-contenv bashio
echo Starting http server!

# debug to check if the addon is reachable from the outside
#python3 -m http.server 8000

python3 web/manage.py runserver 0.0.0.0:8000