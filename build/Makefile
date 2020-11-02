# https://github.com/home-assistant/builder

#docker run --rm --privileged -v ~/.docker:/root/.docker -v $PWD/dev:/data homeassistant/amd64-builder --all -t /data
build_dev:
	docker run --rm --name hassio-builder --privileged \
					-v ${PWD}/dev:/data \
					-v /var/run/docker.sock:/var/run/docker.sock:ro \
					homeassistant/amd64-builder \
						--all \
						--test \
						-t /data

push_dev_all:
	docker push tchr157/activity-assistant-armv7:dev 
	docker push tchr157/activity-assistant-armhf:dev 
	docker push tchr157/activity-assistant-i386:dev 
	docker push tchr157/activity-assistant-amd64:dev 
	docker push tchr157/activity-assistant-aarch64:dev 

push_prod_all:
	docker push tchr157/activity-assistant-armv7:latest
	docker push tchr157/activity-assistant-armhf:latest
	docker push tchr157/activity-assistant-i386:latest 
	docker push tchr157/activity-assistant-amd64:latest
	docker push tchr157/activity-assistant-aarch64:latest

build_armv7_dev:
	docker run --rm -ti --name hassio-builder --privileged \
  	-v ${PWD}/dev:/data \
  	-v /var/run/docker.sock:/var/run/docker.sock:ro \
  	homeassistant/amd64-builder -t /data --armv7 --test \
  	-i tchr157/activity-assistant-{arch}

#build_amd64:
#	cd prod/ && \
#	docker build --build-arg BUILD_FROM="homeassistant/amd64-base:latest" \
#	-t tchr157/activity-assistant-amd64:latest .
#
#build_i386:
#	cd prod/ && \
#	docker build --build-arg BUILD_FROM="homeassistant/i386-base:latest" \
#	-t tchr157/activity-assistant-i386:latest .
