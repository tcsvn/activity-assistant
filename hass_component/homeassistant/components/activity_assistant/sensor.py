




class Person(RestoreEntity):

    def __init__(self, config, editable):
        """Set up person."""
        self._activities = {}
        self._state = None

    @property
    def name(self):
        """Return the name of the entity."""
        return self._config[CONF_NAME]

    @property
    def should_poll(self):
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return False

    @property
    def state(self):
        """Return the state of the person."""
        return self._state

    @property
    def state_attributes(self):
        """Return the state attributes of the person."""
        data = {
            ATTR_EDITABLE: self._editable,
            ATTR_ID: self.unique_id,
        }
        # add activities to attributes
        for key, value in self._activities.items():
            data[key] = value

        user_id = self._config.get(CONF_USER_ID)
        if user_id is not None:
            data[ATTR_USER_ID] = user_id
        return data

    @property
    def unique_id(self):
        """Return a unique ID for the person."""
        return self._config[CONF_ID]


    def person_update_activity(self, activity):
        """Set the persons activity attribute to a value"""
        self._activity = activity
        self._update_state()

    def person_update_activities(self, activities):
        """Set the persons activity attribute to a value"""
        self._activities = activities

    @callback
    def person_updated(self):
        """Handle when the config is updated."""
        self._update_state()

    @callback
    def _update_state(self):
        """Update the state."""
        self._state = self._activity
        self.async_schedule_update_ha_state()

    @callback
    def _parse_source_state(self, state):
        """Parse source state and set person attributes.

        This is a device tracker state or the restored person state.
        """
        self._state = state.state
        #self._latitude = state.attributes.get(ATTR_LATITUDE)
        #self._longitude = state.attributes.get(ATTR_LONGITUDE)
        #self._gps_accuracy = state.attributes.get(ATTR_GPS_ACCURACY)


@websocket_api.websocket_command({
    vol.Required('type'): 'person/list',
})
def ws_list_person(hass: HomeAssistantType,
                   connection: websocket_api.ActiveConnection, msg):
    """List persons."""
    manager = hass.data[DOMAIN]  # type: PersonManager
    connection.send_result(msg['id'], {
        'storage': manager.storage_persons,
        'config': manager.config_persons,
    })


@websocket_api.websocket_command({
    vol.Required('type'): 'person/create',
    vol.Required('name'): vol.All(str, vol.Length(min=1)),
    vol.Optional('user_id'): vol.Any(str, None),
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_create_person(hass: HomeAssistantType,
                           connection: websocket_api.ActiveConnection, msg):
    """Create a person."""
    manager = hass.data[DOMAIN]  # type: PersonManager
    try:
        person = await manager.async_create_person(
            name=msg['name'],
            user_id=msg.get('user_id')
        )
        connection.send_result(msg['id'], person)
    except ValueError as err:
        connection.send_error(
            msg['id'], websocket_api.const.ERR_INVALID_FORMAT, str(err))


@websocket_api.websocket_command({
    vol.Required('type'): 'person/update',
    vol.Required('person_id'): str,
    vol.Required('name'): vol.All(str, vol.Length(min=1)),
    vol.Optional('user_id'): vol.Any(str, None),
    vol.Optional('activity'): str,
    vol.Optional('activities'): dict,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_update_person(hass: HomeAssistantType,
                           connection: websocket_api.ActiveConnection, msg):
    """Update a person."""
    manager = hass.data[DOMAIN]  # type: PersonManager
    changes = {}
    for key in ('name', 'user_id', 'activity', 'activities'):
        if key in msg:
            changes[key] = msg[key]

    try:
        person = await manager.async_update_person(msg['person_id'], **changes)
        connection.send_result(msg['id'], person)
    except ValueError as err:
        connection.send_error(
            msg['id'], websocket_api.const.ERR_INVALID_FORMAT, str(err))


@websocket_api.websocket_command({
    vol.Required('type'): 'person/delete',
    vol.Required('person_id'): str,
})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete_person(hass: HomeAssistantType,
                           connection: websocket_api.ActiveConnection,
                           msg):
    """Delete a person."""
    manager = hass.data[DOMAIN]  # type: PersonManager
    await manager.async_delete_person(msg['person_id'])
    connection.send_result(msg['id'])


def _get_latest(prev: Optional[State], curr: State):
    """Get latest state."""
    if prev is None or curr.last_updated > prev.last_updated:
        return curr
    return prev
