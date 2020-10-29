ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --update python3-dev py3-pip expect \
    jpeg-dev zlib-dev gcc linux-headers musl-dev # to fix pillow error 

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir -p /media/activity_assistant/models /media/activity_assistant/activity_logs /media/activity_assistant/dataset \
    /media/activity_assistant/media

COPY db.sqlite3 /media/activity_assistant/media/db.sqlite3

ENV DJANGO_ENV='development'
WORKDIR /home/
COPY remigrate.exp remigrate.sh run.sh ./
RUN chmod a+x run.sh

CMD [ "./run.sh" ]