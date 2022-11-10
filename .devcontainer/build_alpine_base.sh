#!/bin/bash
docker run --rm --privileged \
    -v ~/.docker:/root/.docker \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    -v $PWD/:/data tchr157/amd64-builder:latest \
    --test \
    --file build/base_alpine/Dockerfile \
    --amd64 --target /data/build/base_alpine
