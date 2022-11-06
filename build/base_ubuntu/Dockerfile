# this is a scikit and pandas environment
ARG BUILD_FROM
FROM $BUILD_FROM
ENV LANG C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get clean  \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.8 \
    python3-pip \
    python3.8-dev \
    libfreetype6 libfreetype6-dev zlib1g-dev \
    libmysqlclient-dev \
    gcc gfortran\
    libopenblas-dev \
    liblapack-dev cython \
    libzbar-dev libzbar0 \
    libffi-dev g++ \
    nginx \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Workdir is '/'
COPY rootfs /

#RUN update-alternatives --remove python /usr/bin/python2 \
#    && update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
RUN python3.8 -m pip install --upgrade pip \
 && pip install --no-cache-dir numpy==1.23.4 --only-binary=:all: --upgrade \
 && pip install --no-cache-dir pandas sklearn
 #&& pip install --no-cache-dir Cython setuptools wheel \

RUN pip install --no-cache-dir -r requirements.txt