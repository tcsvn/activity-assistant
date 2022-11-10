ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

WORKDIR /workspace
COPY rootfs /

RUN apk add --no-cache --update python3-dev py3-pip \
    jpeg-dev zlib-dev gcc linux-headers musl-dev \
    && apk add --no-cache py3-wheel py3-pillow py3-pygments py3-django py3-zeroconf \
    py3-sqlalchemy py3-aiohttp py3-gunicorn py3-pandas \
    py3-scipy py3-scikit-learn py3-matplotlib py3-mysqlclient nginx\
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
    pip3 install --no-cache-dir -r requirements.txt