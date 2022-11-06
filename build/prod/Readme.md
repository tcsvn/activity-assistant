## Knowledge to debug production app

test is django works with

`python3 /etc/opt/activity_assistant/manage.py runserver 0.0.0.0:8000`

test gunicorn standalone with
`gunicorn act_assist.wsgi:application --bind 0.0.0.0:8000`

test gunicorn socket

`gunicorn --bind unix:/run/gunicorn.sock --access-logfile - act_assist.wsgi:application`

and call the socket with

`curl --unix-socket /run/gunicorn.sock localhost`

## Notest

permission of guniconr <-root> vs ngingx nginx
