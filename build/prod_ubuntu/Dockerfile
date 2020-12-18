ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

# todo remove expect
# to fix pillow error 
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.8 \
    python3-pip \
    python3.8-dev \
    libfreetype6 libfreetype6-dev zlib1g-dev \
    gcc gfortran\
    libopenblas-dev \
    liblapack-dev cython \
    && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

#RUN update-alternatives --remove python /usr/bin/python2 \
#    && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN python3.8 -m pip install --upgrade pip 
RUN pip install --no-cache-dir Cython setuptools wheel
COPY build/prod_ubuntu/requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pandas

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
COPY build/prod_ubuntu/start.sh build/prod/initial_server.json ./
RUN chmod a+x start.sh

# copy static files
RUN mkdir -p /var/cache/activity_assistant/static/
RUN python3.8 /opt/activity_assistant/web/manage.py collectstatic
#
CMD [ "./start.sh" ]