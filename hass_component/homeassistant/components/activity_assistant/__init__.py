"""The activity_assistant integration."""
import asyncio
import voluptuous as vol
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN, KEY_HOSTNAME, KEY_WEBHOOK, ZCNF_TYPE, ZCNF_NAME, \
    SERVICE_TRIGGER_DATADMP, SERVICE_TRIGGER_DATADMP_METHOD
from homeassistant.helpers import entity_platform
from .aa_api import ActAssist
from zeroconf import ServiceInfo
from homeassistant.helpers import aiohttp_client
from homeassistant.components.zeroconf import async_get_instance

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)
PLATFORMS = ["binary_sensor"]

def zeroconf_Info2Values(info : ServiceInfo):
    res = {}
    res['port'] = info.port
    res['server'] = info.server
    for key, value in info.properties.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res 

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
    zeroconf = await async_get_instance(hass)
    tmp = zeroconf.get_service_info(ZCNF_TYPE, ZCNF_NAME + '.' + ZCNF_TYPE)
    val_dict = zeroconf_Info2Values(tmp)

    act_assist = ActAssist(
        aiohttp_client.async_get_clientsession(hass),
        val_dict[KEY_HOSTNAME], 
        val_dict['port'],
        val_dict[KEY_WEBHOOK]
    )
    hass.data[DOMAIN].update({entry.entry_id: act_assist})
    _LOGGER.warning("saved ActAssistApi in : " + str(entry.entry_id))

    # create binary state sensor 
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