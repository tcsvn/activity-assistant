ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

WORKDIR /workspace
COPY rootfs /

RUN apt update && apt install -y --no-install-recommends \
    nginx \
    python3.9 python3-pip python3.9-dev \
    # mysqlclient
    default-libmysqlclient-dev libmariadb-dev \ 
    build-essential \
    # Numpy/pandas
    libopenblas-dev \
    libatlas-base-dev \
    # Scipy
    python3-scipy \
    #libatlas3-base libgfortran5 \
    # 
    #gfortran  pkg-config \
    # pkg-config \
    \
    #libssl-dev \
    #libffi-dev \
    #libfreetype6 libfreetype6-dev \
    #libjpeg62-turbo-dev \
    #libpng-dev \
    #libpq-dev \
    #libtiff5-dev \
    #libxml2-dev \
    #libxslt1-dev \
    #libzmq3-dev \
    #zlib1g-dev \
    #gcc \
    #libzbar-dev libzbar0 \
    #openssl \
    #libfreetype6 libfreetype6-dev zlib1g-dev \
    #gcc \
    #liblapack-dev cython \
    #libzbar-dev libzbar0 \
    #libffi-dev g++ \
    && python3 -m pip install --no-cache-dir --upgrade pip \
    && python3 -m pip install --no-cache-dir -r requirements.txt \ 
    \
    && apt clean  \
    && apt purge -y --auto-remove \
    python3.9-dev \
    \
    #
    && python3 test_import.py \
    && rm /workspace/* \
    && find /usr/local \
    \( -type d -a -name test -o -name tests -o -name '__pycache__' \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' + \
    \
    && rm -fr \
    /tmp/* \
    /root/{.cache,.config,.gnupg,.local,.log,.npm} \
    /usr/local/share/.cache \
    /var/{cache,log}/* \
    /var/lib/apt/lists/* \
    \
    # Do this for nginx to work
    && adduser --system --no-create-home --shell /bin/false --group --disabled-login nginx \
    && mkdir /var/log/nginx \
    && chown -R nginx:nginx /var/log/nginx \
    && chmod -R 755 /var/log/nginx
