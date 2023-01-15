#!/usr/bin/env bashio

DJANGO_USER="root"
DJANGO_PROJECT="activity_assistant"


cd /opt/$DJANGO_PROJECT/web
export PYTHONPATH=/etc/opt/$DJANGO_PROJECT:/opt/$DJANGO_PROJECT
export DJANGO_SETTINGS_MODULE=settings


# Start Gunicorn processes in background
# 5 minutes of timeout,
# 2 workers since 4 use to much memory on 1GB rpi3 armv7
# restart workers every 20 request since workers do not free memory allocated at peaks
# restart jittoer of 10% reduces restart load
gunicorn act_assist.wsgi:application --bind unix:/run/gunicorn.sock \
--keep-alive 300 \
--timeout 300 \
--workers 2 \
--max-requests 20 \
--max-requests-jitter 2 \
-e PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant:/opt/activity_assistant/web:/etc/opt/activity_assistant/act_assist \
-e SUPERVISOR_TOKEN=$SUPERVISOR_TOKEN \
-e DJANGO_ENV=production \
-e TZ=$TZ \
-e HASSIO_TOKEN=$HASSIO_TOKEN \
-e DJANGO_SETTINGS_MODULE=settings &


# start nginx in foreground
/usr/sbin/nginx -g "daemon off; pid /tmp/nginx.pid;"
sleep infinity