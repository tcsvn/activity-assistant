# activity-assistant
Activity assistant provides a platform for logging and predicting Activities of Daily Living (ADLs) in realtime for home assistant users. 



## Development
##### Steps
    - in vscode type the command `remote-container open folder in container` in the directory root. This opens up the station
    - go to folder `/workspaces/test_hassio/addons/local` to find all the project related files
    - make start_ha.sh executable with `chmod +x /usr/local/bin/start_ha.sh`
    - start supervisor with `strg+umschalt+B` and run task `run Homeassistant`

### workflow
    - with `docker exec -ti hassio_cli /usr/bin/cli.sh` open ha 
    1. change sth with the addon
    2. update version number in config.json
    3. in cli type `addons reload`
    4. goto 1. 
