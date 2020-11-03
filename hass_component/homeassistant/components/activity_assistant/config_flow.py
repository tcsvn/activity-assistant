from homeassistant import config_entries
from homeassistant.helpers import config_entry_flow
from . import call_webhook
from homeassistant.components.zeroconf import async_get_instance
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from zeroconf import ServiceInfo
from .const import DOMAIN, KEY_HOSTNAME, KEY_HOSTNAME, ZCNF_TYPE, ZCNF_NAME
import logging


_LOGGER = logging.getLogger(__name__)


def zeroconf_Info2Values(info : ServiceInfo):
    res = {}
    res['port'] = info.port
    res['server'] = info.server
    for key, value in info.properties.items():
        res[key.decode("utf-8")] = value.decode("utf-8")
    return res 


async def _async_has_devices(hass) -> bool:
    """Return if there are devices that can be discovered."""
    # check if the api is reachable
    # try to read the devices from 
    zeroconf = await async_get_instance(hass)
    tmp = zeroconf.get_service_info(ZCNF_TYPE, ZCNF_NAME + '.' + ZCNF_TYPE)
    val_dict = zeroconf_Info2Values(tmp)
    webhook_url = 'http://' + val_dict[KEY_HOSTNAME] \
        + ':' + val_dict['port'] +  val_dict[KEY_WEBHOOK]
    _LOGGER.warning(str(val_dict))
    _LOGGER.warning(webhook_url)

    async with async_get_clientsession(hass) as session: 
        async with session.get(webhook_url) as resp:
            _LOGGER.warning('resp: ', str(resp))
            _LOGGER.warning('resp status: ', str(resp.status))
            return resp.status == 200


config_entry_flow.register_discovery_flow(
    DOMAIN, "Activity Assistant", _async_has_devices, config_entries.CONN_CLASS_LOCAL_PUSH
)