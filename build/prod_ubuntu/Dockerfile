ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

ENV DJANGO_ENV='production'
ENV DJANGO_DEBUG=false
ENV PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant


COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pyadlml

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
COPY build/prod_ubuntu/start.sh build/prod/initial_server.json ./
RUN chmod a+x start.sh

# copy static files
RUN mkdir -p /var/cache/activity_assistant/static/
RUN python3.8 /opt/activity_assistant/web/manage.py collectstatic
#
CMD [ "./start.sh" ]