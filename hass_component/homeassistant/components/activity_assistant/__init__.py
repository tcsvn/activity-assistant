"""The activity_assistant integration."""
import asyncio
import voluptuous as vol
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN
from homeassistant.helpers import entity_platform

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
PLATFORMS = ["binary_sensor"]
SERVICE_TRIGGER_DATADMP = 'trigger_data_dump'
SERVICE_TRIGGER_DATADMP_METHOD = 'async_trigger_data_dump'

def call_webhook():
    import requests
    tmp = requests.get('http://local-act-assist:8000/api/v1/dataset/webhook')

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the activity_assistant component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """activity assistant form a config entry 
    is only called once the whole magic has to happen here
    """

    #_LOGGER.warning(str(entry.version))
    #_LOGGER.warning(str(entry.entry_id))
    #_LOGGER.warning(str(entry.title))
    #_LOGGER.warning(str(entry.data))
    #_LOGGER.warning(str(entry.source))
    #_LOGGER.warning(str(entry.connection_class))
    hass.data.setdefault(DOMAIN, {})
    act_assist_api = await act_assist_api_setup(
        hass, 'asdf', 9000
    )
    hass.data[DOMAIN].update({entry.entry_id: act_assist_api})

    # create binary sensor 
    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def act_assist_api_setup(hass, host, port):
    """Create an Activity assistance instance only once."""
    api = ActAssistApi(host, port)

    return api


class ActAssistApi():
    """Keep the Act instance in one place and centralize the update."""

    def __init__(self, host, port):
        """Initialize the Daikin Handle."""
        self._host = "http://localhost"
        self._port = 8000

        self._url = {
            "webhook": host + ':' + "/api/v1/dataset/webhook"
        }

    async def async_update(self, **kwargs):
        """Pull the latest data from Daikin."""
        pass
        #try:
        #    await self.device.update_status()
        #    self._available = True
        #except ClientConnectionError:
        #    _LOGGER.warning("Connection failed for %s", self.ip_address)
        #    self._available = False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return {}
        #return {
        #    "connections": {(CONNECTION_NETWORK_MAC, self.device.mac)},
        #    "manufacturer": "Daikin",
        #    "model": info.get("model"),
        #    "name": info.get("name"),
        #    "sw_version": info.get("ver", "").replace("_", "."),
        #}