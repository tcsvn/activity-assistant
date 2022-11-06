ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

WORKDIR /home

COPY rootfs /

RUN apk add --no-cache --update python3-dev py3-pip \
    jpeg-dev zlib-dev gcc linux-headers musl-dev \
 && apk add --no-cache py3-wheel py3-pillow py3-pygments py3-django py3-zeroconf \
    py3-sqlalchemy py3-aiohttp py3-numpy py3-gunicorn py3-pandas  \
    py3-scipy py3-scikit-learn py3-mysqlclient nginx\
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community


RUN pip3 install --no-cache-dir -r requirements.txt

ENV DJANGO_ENV='production'
ENV PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant
#               for act_assist/..           for web/.. hass_api/..  for app frontend/.. backend/.. for settings.py
ENV PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant:/opt/activity_assistant/web:/etc/opt/activity_assistant/act_assist
# Copy program files
COPY web/ /opt/activity_assistant/web/
COPY hass_api/ /opt/activity_assistant/hass_api/

COPY services/* /opt/activity_assistant/

# Copy configuration files
COPY web/act_assist/settings.py  /etc/opt/activity_assistant/
COPY web/act_assist/local_settings/ /etc/opt/activity_assistant/local_settings/

# Configure nginx & gunicorn
#RUN rm /etc/nginx/conf.d/default.conf  TODO

# copy static files
RUN chmod a+x start.sh \
 && mkdir -p /var/cache/activity_assistant/static/ \
 && python3 /opt/activity_assistant/web/manage.py collectstatic

ENTRYPOINT ["/bin/bash", "/home/entrypoint.sh"]

CMD [ "/bin/bash", "/home/start.sh" ]
