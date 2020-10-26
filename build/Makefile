tag_gitlab_x86:
	docker tag hassbrain_web:dev registry.gitlab.com/hassbrain/hassbrain_web:x86

tag_gitlab_arm:
	docker tag hassbrain_web:armv7 registry.gitlab.com/hassbrain/hassbrain_web:armv7

build_x86_base:
	docker pull python:3.7.0-slim
	docker build -f x86/Dockerfile.base -t registry.gitlab.com/hassbrain/hassbrain_web/x86:base ../

build_x86_app:
	docker build --no-cache -f x86/Dockerfile -t registry.gitlab.com/hassbrain/hassbrain_web/x86:latest ../

build_arm_base:
	docker pull arm32v7/python:3.7.3-slim
	docker build --no-cache -f arm/Dockerfile.base -t registry.gitlab.com/hassbrain/hassbrain_web/arm:base ../

build_arm_app:
#	docker build --no-cache -f arm/Dockerfile -t registry.gitlab.com/hassbrain/hassbrain_web/arm:latest ../
	docker build -f arm/Dockerfile -t registry.gitlab.com/hassbrain/hassbrain_web/arm:latest ../


#----------------------------------------------------------------------------------------------------------------
tag_arm_dev:
	docker tag registry.gitlab.com/hassbrain/hassbrain_web/arm:latest hassbrain_web:dev

tag_x86_dev:
	docker tag registry.gitlab.com/hassbrain/hassbrain_web/x86:latest hassbrain_web:dev

#----------------------------------------------------------------------------------------------------------------
bash:
	docker run --rm -ti \
	hassbrain_web:dev /bin/bash

run:
	docker run --rm -ti \
	--name dev_hb_web \
	-v /home/cmeier/code/data/datasets:/home/data/datasets \
	-v /home/cmeier/code/data/hb_models:/home/data/hb_models \
	-v /home/cmeier/code/data/activity_logs:/home/data/activity_logs \
	-p 8000:8000 \
	registry.gitlab.com/hassbrain/hassbrain_web/arm:latest

exec_bash:
	docker exec -ti dev_hb_web /bin/bash 

run2:
	docker run --rm -ti \
	-v $$(pwd)/../hassbrain_rest/hassbrain_web:/home/hassbrain_rest/hassbrain_web \
	-p 8000:8000 \
	hassbrain_web:dev

run3:
	docker run --rm -ti \
	-p 9000:8000 \
	hassbrain_web:dev

debug:
	docker run --rm -ti \
	-v $$(pwd)/hassbrain_rest:/home/hassbrain_rest/ \
	-v $$(pwd)/datasets:/home/datasets \
	-v $$(pwd)/hb_models:/home/hb_models \
	-v $$(pwd)/../hassbrain_algorithm/hassbrain_algorithm:/usr/local/lib/python3.7/site-packages/hassbrain_algorithm/ \
	-v $$(pwd)/../hassbrain_api/hassbrainApi:/usr/local/lib/python3.7/site-packages/hassbrainApi/ \
	-v $$(pwd)/../homeassistant_api/homeassistant_api:/usr/local/lib/python3.7/site-packages/homeassistant_api/ \
	-p 8000:8000 \
	hassbrain_web:dev
