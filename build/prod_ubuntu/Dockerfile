ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

ENV DJANGO_ENV='production'
ENV PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant

# TO DELETE START
# do this to look if things work out for arm
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmysqlclient-dev \
    && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*
RUN pip install ruamel.yaml mysqlclient
# TO DELETE END

# install relevant files
RUN pip install --no-cache pyadlml

# copy program files
COPY web/ /opt/activity_assistant/web/ 
COPY hass_api/ /opt/activity_assistant/hass_api/
COPY services/* /opt/activity_assistant/

# copy configuration files
COPY web/act_assist/settings.py  /etc/opt/activity_assistant/
COPY web/act_assist/local_settings/ /etc/opt/activity_assistant/local_settings/

# configure nginx & gunicorn
COPY build/prod_ubuntu/nginx.conf /etc/nginx/conf.d

WORKDIR /home
COPY build/prod_ubuntu/start.sh build/prod/initial_server.json ./
RUN chmod a+x start.sh
#
## copy static files
RUN mkdir -p /var/cache/activity_assistant/static/ \
 && python3.8 /opt/activity_assistant/web/manage.py collectstatic \
 && ln -sf /usr/bin/python3.8 /usr/bin/python3
# link python3 to python3.8 because starting a python script in ubuntu
# launches 3.6 system python and doesn't work

CMD [ "./start.sh" ]