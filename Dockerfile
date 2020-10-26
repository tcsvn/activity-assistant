# Note: this is a development container

ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --update python3-dev py3-pip expect \
    jpeg-dev zlib-dev gcc linux-headers musl-dev # to fix pillow error 

COPY build/dev/requirements.txt .
RUN pip3 install -r requirements.txt

# TODO remove stuff for building that bloats the image
RUN mkdir -p /home/data/models /home/data/activity_logs /home/data/dataset \
    /home/data/media

COPY build/dev/db.sqlite3 /home/data/media/db.sqlite3

# development stuff
WORKDIR /home/tmp

# Copy data for add-on
COPY build/dev/ .

RUN	./remigrate.exp
#RUN python3 manage.py loaddata tmp_debug_fixtures.json

ENV DJANGO_ENV='development'

# as the addon maps the data already into the container 
WORKDIR /addons
COPY run.sh .
RUN chmod a+x run.sh

CMD [ "./run.sh" ]