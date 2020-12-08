ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --update python3-dev py3-pip \
    jpeg-dev zlib-dev gcc linux-headers musl-dev # to fix pillow error 

# pandas needs very long to intall over pip (has to be built)
# therefore install from package repo
# TODO remove --repository when this is in stable
RUN apk add py3-wheel py3-pillow py3-pygments py3-django py3-zeroconf \
    py3-sqlalchemy py3-aiohttp py3-gunicorn py3-pandas py3-kiwisolver \
    py3-scipy py3-scikit-learn py3-matplotlib \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community

COPY requirements.txt .
RUN pip3 install -r requirements.txt

ENV DJANGO_ENV='development'
WORKDIR /home/
COPY run.sh zero_conf_browser.py initial_server.json ./
RUN chmod a+x run.sh

CMD [ "./run.sh" ]