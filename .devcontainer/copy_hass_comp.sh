#!/bin/bash
docker cp /workspaces/test_hassio/share/hass_component/homeassistant/ homeassistant:/usr/src/homeassistant/
docker exec hassio_cli ha core restart