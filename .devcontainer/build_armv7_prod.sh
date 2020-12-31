
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes


docker run --rm --privileged \
    -v ~/.docker:/root/.docker \
    -v /var/run/docker.sock:/var/run/docker.sock:ro \
    -v $PWD/:/data tchr157/armv7-builder \
    --test \
    --file build/prod_ubuntu/Dockerfile \
    --armv7 --target /data
 