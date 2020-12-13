ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# todo remove expect
# to fix pillow error 
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-dev \
    gcc gfortran\
    libopenblas-dev \
    liblapack-dev cython \
    && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

#RUN apk add --update python3-dev py3-pip expect \ 
#    jpeg-dev zlib-dev gcc linux-headers musl-dev 
RUN pip3 install --no-cache-dir Cython
COPY build/prod_debian/requirements.txt .
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