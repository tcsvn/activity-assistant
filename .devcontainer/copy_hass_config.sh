#!/bin/bash
docker cp "$(pwd)/.devcontainer/config_dummies.yaml" homeassistant:/config/configuration.yaml
docker exec hassio_cli ha core restart