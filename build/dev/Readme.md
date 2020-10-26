# Maintenance

* activate the virtual env for python type 'source django-test/bin/activate'
* start testserver by typing `python manage.py runserver`


# API

#### CLI

### Get an Entry
curl --user test:asdf http://localhost:8000/api/v1/?format=json

### Create an Entry
`curl -X POST --user test:asdf http://localhost:8000/api/v1/persons/ -H "Content-Type: application/json" -d '{ "name":"chris", "device": "http://localhost:8000/api/v1/devices/1/", "logging": false, "logged_activity": "http://localhost:8000/api/v1/activities/2/", "logged_location":"nothing", "predicted_activity":"kitchen", "predicted_location":"kitchen"}'`

### Delete an Entry
curl -i -X DELETE http://localhost:8000/api/v1/activities/1/

### Update an Entry
* it doesn't has to be the whole entry 
curl -X PUT --user test:asdf http://localhost:8000/api/v1/persons/1/ -H "Content-Type: application/json" -d '{ "name":"chris", "device": "http://localhost:8000/api/v1/devices/1/", "logging": false, "logged_activity": "http://localhost:8000/api/v1/activities/2/"}'


### 
