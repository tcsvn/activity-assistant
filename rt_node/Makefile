build_nc:
	docker pull python:3.7.0-slim
	docker pull python:3.7.0 #todo remove
	docker build --no-cache -t hassbrain_web:dev .

build:
	docker pull python:3.7.0-slim
	docker build -t hassbrain_web:dev .

remigrate:
	docker run --rm -ti \
	-v $$(pwd)/hassbrain_rest:/home/hassbrain_rest/ \
	-v $$(pwd)/../hassbrain_algorithm/hassbrain_algorithm:/usr/local/lib/python3.7/site-packages/hassbrain_algorithm/ \
	-p 8000:8000 \
	hassbrain_web:dev \
	./remigrate.exp
	#/bin/bash
	#/bin/bash remigrate.sh

create_dummys:
	bash hassbrain_rest/create_dummys.sh

run:
	docker run --rm -ti \
	-v $$(pwd)/hassbrain_rest:/home/hassbrain_rest/ \
	-v $$(pwd)/datasets:/home/datasets \
	-v $$(pwd)/hb_models:/home/hb_models \
	-v $$(pwd)/../hassbrain_algorithm/hassbrain_algorithm:/usr/local/lib/python3.7/site-packages/hassbrain_algorithm/ \
	-v $$(pwd)/../hassbrain_api/hassbrainApi:/usr/local/lib/python3.7/site-packages/hassbrainApi/ \
	-p 8000:8000 \
	hassbrain_web:dev

both:
	docker-compose up

debug2:
	docker run --rm -ti \
	-p 8000:8000 \
	-v $$(pwd)/../hassbrain_algorithm/hassbrain_algorithm:/usr/local/lib/python3.7/site-packages/hassbrain_algorithm/ \
	-v $$(pwd)/hassbrain_rest:/home/hassbrain_rest/ \
	hassbrain_web:dev /bin/bash
