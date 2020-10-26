curl -X POST --user admin:asdf http://localhost:8000/api/v1/server/ -H "Content-Type: application/json" -d '{ "server_address": "http://134.2.56.122:8000", "hass_address": "http://134.2.56.122:8123", "hass_api_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkN2Q1ODZlODRmZTM0NGUyYTE0ZTc5ZTc2ODExZGE2MiIsImlhdCI6MTU1NDkxMzI3NSwiZXhwIjoxODcwMjczMjc1fQ.9aDP7bdxXqmRpndL4yV5B-65W2C0vgLziLskKEZ7fAA", "selected_algorithm":null, "realtime_node":null}' 

curl -X POST --user admin:asdf http://localhost:8000/api/v1/activities/ -H "Content-Type: application/json" -d '{ "name": "cooking" }' 
curl -X POST --user admin:asdf http://localhost:8000/api/v1/activities/ -H "Content-Type: application/json" -d '{ "name": "eating" }' 
curl -X POST --user admin:asdf http://localhost:8000/api/v1/activities/ -H "Content-Type: application/json" -d '{ "name": "sleeping" }' 

curl -X POST --user admin:asdf http://localhost:8000/api/v1/locations/ -H "Content-Type: application/json" -d '{ "name": "kitchen", "node_id" : 1 , "x": 400, "y": 500}'
curl -X POST --user admin:asdf http://localhost:8000/api/v1/locations/ -H "Content-Type: application/json" -d '{ "name": "toilet", "node_id" : 2 ,  "x": 400, "y": 400}'
curl -X POST --user admin:asdf http://localhost:8000/api/v1/locations/ -H "Content-Type: application/json" -d '{ "name": "bedroom", "node_id" : 3 , "x": 500, "y": 500}'

curl -X POST --user admin:asdf http://localhost:8000/api/v1/edges/ -H "Content-Type: application/json" -d '{ "source" : "http://localhost:8000/api/v1/locations/2/", "sink" : "http://localhost:8000/api/v1/locations/1/" }'


#curl -X POST --user admin:asdf http://localhost:8000/api/v1/persons/ -H "Content-Type: application/json" -d '{ "name":"chris", "prediction":false, "smartphone":"", "predicted_activity":"http://localhost:8000/api/v1/activities/2/", "predicted_location":"http://localhost:8000/api/v1/locations/2/"}'
#
#curl -X POST --user admin:asdf http://localhost:8000/api/v1/smartphones/ -H "Content-Type: application/json" -d '{ "name": "nexus4", "logging": false, "synchronized":false, "person":"http://localhost:8000/api/v1/persons/1/" ,"logged_activity": "http://localhost:8000/api/v1/activities/1/", "logged_location":"http://localhost:8000/api/v1/locations/2/"}'

curl -X POST --user admin:asdf http://localhost:8000/api/v1/devicecomponents/ -H "Content-Type: application/json" -d '{ "name" : "light"}'
curl -X POST --user admin:asdf http://localhost:8000/api/v1/devicecomponents/ -H "Content-Type: application/json" -d '{ "name" : "binary_sensor"}'
curl -X POST --user admin:asdf http://localhost:8000/api/v1/devicecomponents/ -H "Content-Type: application/json" -d '{ "name" : "switch"}'

curl -X POST --user admin:asdf http://localhost:8000/api/v1/devices/ -H "Content-Type: application/json" -d '{ "name" : "tradfri_mirror", "state" : "on", "location" : "http://localhost:8000/api/v1/locations/1/", "component" : "http://localhost:8000/api/v1/devicecomponents/1/"}'

curl -X POST --user admin:asdf http://localhost:8000/api/v1/devices/ -H "Content-Type: application/json" -d '{ "name" : "pir_motion", "state" : "on", "location" : "http://localhost:8000/api/v1/locations/1/", "component" : "http://localhost:8000/api/v1/devicecomponents/2/"}'
curl -X POST --user admin:asdf http://localhost:8000/api/v1/devices/ -H "Content-Type: application/json" -d '{ "name" : "computer", "state" : "on", "location" : "http://localhost:8000/api/v1/locations/1/", "component" : "http://localhost:8000/api/v1/devicecomponents/3/"}'

text="Hidden Markov Model is a statistical Markov model in which the system being modeled is assumed to be a Markov process with unobserved states. Hidden Markov Model is a statistical Markov model in which the system being modeled is assumed to be a Markov process with unobserved states. Hidden Markov Model is a statistical Markov model in which the system being modeled is assumed to be a Markov process with unobserved states."

curl -X POST --user admin:asdf http://localhost:8000/api/v1/algorithms/ -H "Content-Type: application/json" -d "{ \"name\": \"HMM_LC\", \"class_name\": \"ModelHMM_log_scaled\", \"description\" : \"$text\",  \"multiple_person\" : \"False\", \"unsupervised\" : \"False\", \"activity_duration\" : \"False\", \"location\" : \"False\", \"model\" : null, \"train_dataset\" : null, \"benchmark\": null }"

curl -X POST --user admin:asdf http://localhost:8000/api/v1/algorithms/ -H "Content-Type: application/json" -d "{ \"name\": \"HMM\", \"class_name\": \"ModelHMM\", \"description\" : \"$text\",  \"multiple_person\" : \"False\", \"unsupervised\" : \"False\", \"activity_duration\" : \"False\", \"location\" : \"False\", \"model\" : null, \"train_dataset\" : null, \"benchmark\": null }"

curl -X POST --user admin:asdf http://localhost:8000/api/v1/datasets/ -H "Content-Type: application/json" -d "{ \"name\" : \"kasteren\", \"path_to_sensor_data\" : null,  \"path_to_activity_data\" : null, \"path_to_database\" : null }"
curl -X POST --user admin:asdf http://localhost:8000/api/v1/datasets/ -H "Content-Type: application/json" -d "{ \"name\" : \"homeassistant\", \"path_to_sensor_data\" : null,  \"path_to_activity_data\" : null, \"path_to_database\" : null }"
curl -X POST --user admin:asdf http://localhost:8000/api/v1/datasets/ -H "Content-Type: application/json" -d "{ \"name\" : \"mavlab\", \"path_to_sensor_data\" : null,  \"path_to_activity_data\" : null, \"path_to_database\" : null }"


