from datetime import timedelta
import logging
from homeassistant.components.binary_sensor import (
    BinarySensorEntity, DEVICE_CLASS_CONNECTIVITY
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform

from .const import DOMAIN
_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)
SERVICE_TRIGGER_DATADMP = 'trigger_data_dump'
SERVICE_TRIGGER_DATADMP_METHOD = 'async_trigger_data_dump'

async def async_setup_entry(hass, entry, async_add_entitites):

    _LOGGER.warning(str(entry.title))
    _LOGGER.warning('lulu'*10)

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(SERVICE_TRIGGER_DATADMP,
     {},SERVICE_TRIGGER_DATADMP_METHOD)

    sensors = [Logging()]
    async_add_entitites(sensors, True)


class Logging(BinarySensorEntity):
    """Observes the connectivity of the Addon
        but more important the update of the sensor
        and triggers the  
        polling the webhook
    """

    def __init__(self):
        self._name = "Act assist Logging"
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
        # TODO call webhook from homeassistant
        # TODO set SCAN_INTERVAL to appropriate value
        import requests
        #{REPO}_{SLUG}
        # REPO is local
        # SLug is act_assist
        # turn all _ to -
        #tmp = requests.get('http://local_act_assist:8000/api/v1/dataset/webhook')
        #tmp = requests.get('http://local-act-assist:8000/api/v1/')
        tmp ='asdf'
        _LOGGER.warning("BS AA: --- "  + str(tmp))
        #session = hass.helpers.aiohttp_client.async_get_clientsession()
        #    try:
        #        with timeout(TIMEOUT):
        #            device = await Appliance.factory(
        #                host, session, key=key, uuid=uuid, password=password
        #            )
        #    except asyncio.TimeoutError as err:
        #        _LOGGER.debug("Connection to %s timed out", host)
        #        raise ConfigEntryNotReady from err
        #    except ClientConnectionError as err:
        #        _LOGGER.debug("ClientConnectionError to %s", host)
        #        raise ConfigEntryNotReady from err
        #    except Exception:  # pylint: disable=broad-except
        #        _LOGGER.error("Unexpected error creating device %s", host)
        #        return None

