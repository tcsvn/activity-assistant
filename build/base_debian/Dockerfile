ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

WORKDIR /workspace
COPY rootfs /

RUN apt update && apt install -y --no-install-recommends \
    python3.10 python3-pip python3.10-dev \
    default-libmysqlclient-dev \
    build-essential \
    nginx \
    && python3 -m pip install --no-cache-dir --upgrade pip
#RUN python3 -m pip install --no-cache-dir --only-binary=:all: -r requirements_binary.txt \
RUN python3 -m pip install --no-cache-dir -r requirements_binary.txt \
    && python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt clean  \
    && apt purge -y --auto-remove \
    build-essential \
    python3.10-dev \
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
    /var/lib/apt/lists/*




#RUN apt-get purge -y --auto-remove \
#        build-essential \
#        dirmngr \
#        gpg \
#        gpg-agent \
#        libffi-dev \
#        libfreetype6-dev \
#        libjpeg62-turbo-dev \
#        libmariadb-dev \
#        libpng-dev \
#        libpq-dev \
#        libssl-dev \
#        libtiff5-dev \
#        libxml2-dev \
#        libxslt1-dev \
#        libzmq3-dev \
#        pkg-config \
#        python-dev \
#        python3-dev \
#        zlib1g-dev \
#    \


#RUN apt-get update && apt-get install -y --no-install-recommends \
#    python3.8 \
#    python3-pip \
#    python3.8-dev \
#    libfreetype6 libfreetype6-dev zlib1g-dev \
#    gcc gfortran\
#    libopenblas-dev \
#    liblapack-dev cython \
#    libzbar-dev libzbar0 \
#    libffi-dev g++ \
#    nginx \
# && apt-get clean \
# && rm -rf /var/lib/apt/lists/*

# Workdir is '/'

#RUN update-alternatives --remove python /usr/bin/python2 \
#    && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
#RUN python3.8 -m pip install --upgrade pip \
# && pip install --no-cache-dir numpy==1.23.4 --only-binary=:all: --upgrade \
# && pip install --no-cache-dir pandas sklearn
# #&& pip install --no-cache-dir Cython setuptools wheel \

#RUN pip install --no-cache-dir -r requirements.txt