from datetime import timedelta
import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity, DEVICE_CLASS_CONNECTIVITY
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
import aiohttp
from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)
SERVICE_TRIGGER_DATADMP = 'trigger_data_dump'
SERVICE_TRIGGER_DATADMP_METHOD = 'async_trigger_data_dump'

async def async_setup_entry(hass, entry, async_add_entitites):
    """ creates one logging sensor and a service for the webhook
    """
    act_assist = hass.data[DOMAIN][entry.entry_id]

    # register service for the webhook 
    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_TRIGGER_DATADMP,
        {},
        SERVICE_TRIGGER_DATADMP_METHOD)

    async_add_entitites([Logging(act_assist)], True)
    _LOGGER.warning('setup binary sensors: ' + str(entry.title))

class Logging(BinarySensorEntity):
    """Observes the connectivity of the Addon
        but more important the update of the sensor
        and triggers the  
        polling the webhook
    """

    def __init__(self, act_assist):
        self._name = "Act assist Logging"
        self._act_assist = act_assist
        self._state = False

    @property
    def name(self):
        """Return the name of the binary sensor."""
        return self._name
    
    @property
    def should_poll(self):
        """Tells homeassistant that I call the updates"""
        return True

    @property
    def is_on(self):
        """Return if the binary sensor is turned on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of this device, from component DEVICE_CLASSES."""
        return DEVICE_CLASS_CONNECTIVITY

    @property
    def device_info(self):
        """Return the device info for this binary sensor."""
        return {}

    async def async_trigger_data_dump(self):
        _LOGGER.warning("triggered data dump")

    async def async_update(self):
        """ calls webhook of Activity-assistant
        """
        try:
            status = await self._act_assist.call_webhook()
            _LOGGER.warning('Scanning...')
        except aiohttp.ClientError:
            _LOGGER.warning('Webhook threw exception ')

        # TODO set SCAN_INTERVAL to appropriate value
        poll_int = await self._act_assist.get_scan_interval()
        _LOGGER.warning('New Scanint: ' + str(poll_int))
        SCAN_INTERVAL = poll_int