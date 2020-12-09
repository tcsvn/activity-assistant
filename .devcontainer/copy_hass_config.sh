#!/bin/bash
docker cp /workspaces/test_hassio/share/build/dev/config_dummies.yaml homeassistant:/config/configuration.yaml
docker exec hassio_cli ha core restart