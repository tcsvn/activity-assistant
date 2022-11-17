#!/usr/bin/env bashio

DJANGO_USER="root"
DJANGO_PROJECT="activity_assistant"


cd /opt/$DJANGO_PROJECT/web
export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT
export DJANGO_SETTINGS_MODULE=settings


# Start Gunicorn processes in background
gunicorn act_assist.wsgi:application --bind unix:/run/gunicorn.sock \
--keep-alive 300 \
--timeout 300 \
--workers 4 \
-e PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant:/opt/activity_assistant/web:/etc/opt/activity_assistant/act_assist \
-e SUPERVISOR_TOKEN=$SUPERVISOR_TOKEN \
-e DJANGO_ENV=production \
-e TZ=$TZ \
-e HASSIO_TOKEN=$HASSIO_TOKEN \
-e DJANGO_SETTINGS_MODULE=settings &


# start nginx in foreground
/usr/sbin/nginx -g "daemon off; pid /tmp/nginx.pid;"
sleep infinity