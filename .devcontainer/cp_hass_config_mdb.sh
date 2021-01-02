#!/bin/bash
# copies  config_dummies_mariadb.yaml to homeassistant 
docker cp /workspaces/test_hassio/share/.devcontainer/config_dummies_mariadb.yaml homeassistant:/config/configuration.yaml
docker exec hassio_cli ha core restart