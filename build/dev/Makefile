remigrate:
	./remigrate.exp

populate_database:
	python3 manage.py loaddata dev/fixtures_debug2.json

create_dummys:
	/bin/bash dev/create_dummys.sh

run:
	mkdir -p /tmp/activity-assistant/
	sudo mkdir -p /tmp/activity-assistant/act_assist_rest/
	sudo chmod 777 /tmp/activity-assistant/
	sudo chmod 777 /tmp/activity-assistant/act_assist_rest/
	bash runserver.sh


makemigrate:
	cd ../ && python3 web/manage.py makemigrations
