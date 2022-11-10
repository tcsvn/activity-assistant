#!/bin/bash
# CAVE: execute in workdir 

docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
ln -s build/prod_debian/build.json build.json
ln -s build/prod_debian/config.json config.json

docker run --rm --privileged \
    -v ~/.docker:/root/.docker \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    -v $PWD/:/data tchr157/armv7-builder \
    --test \
    --file build/prod_debian/Dockerfile \
    --armv7 --target /data

rm build.json config.json
 