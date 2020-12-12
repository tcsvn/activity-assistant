ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# todo remove expect
# to fix pillow error 
RUN apk add --update python3-dev py3-pip expect \ 
    jpeg-dev zlib-dev gcc linux-headers musl-dev 

# pandas needs very long to intall over pip (has to be built)
# therefore install from package repo
# TODO remove --repository when this is in stable
RUN apk add py3-wheel py3-pillow py3-pygments py3-django py3-zeroconf \
    py3-sqlalchemy py3-aiohttp py3-gunicorn py3-pandas py3-kiwisolver \
    py3-scipy py3-scikit-learn py3-matplotlib \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

COPY build/prod/requirements.txt .
RUN pip3 install -r requirements.txt

ENV DJANGO_ENV='production'
ENV DJANGO_DEBUG=false
ENV PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant

# copy program files
COPY web/ /opt/activity_assistant/web/ 
COPY hass_api/ /opt/activity_assistant/hass_api/

#COPY web/frontend/static/ /var/cache/activity_assistant/static/
#COPY web/frontend/templates/ /var/cache/activity_assistant/static/templates/
COPY services/* /opt/activity_assistant/

# copy configuration files
COPY web/act_assist/settings.py  /etc/opt/activity_assistant/
COPY web/act_assist/local_settings/ /etc/opt/activity_assistant/local_settings/

WORKDIR /home
COPY build/prod/start.sh build/prod/initial_server.json ./
RUN chmod a+x start.sh

# copy static files
RUN mkdir -p /var/cache/activity_assistant/static/
RUN python3 /opt/activity_assistant/web/manage.py collectstatic

CMD [ "./start.sh" ]