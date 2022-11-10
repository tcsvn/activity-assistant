ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

# Install relevant files
WORKDIR /home
COPY build/prod/rootfs /
RUN pip install --no-cache pyadlml


ENV DJANGO_ENV='production'
ENV PYTHONPATH=/etc/opt/activity_assistant:/opt/activity_assistant:/opt/activity_assistant/web:/etc/opt/activity_assistant/act_assist


# Copy program files
COPY web/ /opt/activity_assistant/web/
COPY hass_api/ /opt/activity_assistant/hass_api/
COPY services/* /opt/activity_assistant/

# Copy configuration files
COPY web/act_assist/settings.py  /etc/opt/activity_assistant/
COPY web/act_assist/local_settings/ /etc/opt/activity_assistant/local_settings/

# Copy static files
RUN chmod a+x start.sh \
    && mkdir -p /var/cache/activity_assistant/static/ \
    && python3 /opt/activity_assistant/web/manage.py collectstatic

ENTRYPOINT ["/bin/bash", "/home/entrypoint.sh"]

CMD [ "/bin/bash", "/home/start.sh" ]

