#!/bin/bash

# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn hassbrain_web.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 100
