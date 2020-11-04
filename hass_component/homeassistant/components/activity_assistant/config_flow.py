from homeassistant import config_entries
from homeassistant.helpers import config_entry_flow
from homeassistant.components.zeroconf import async_get_instance
from homeassistant.helpers import aiohttp_client
from zeroconf import ServiceInfo
from .const import DOMAIN, KEY_HOSTNAME, KEY_WEBHOOK, ZCNF_TYPE, ZCNF_NAME
import logging
import aiohttp
from .aa_api import ActAssist
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
    zeroconf = await async_get_instance(hass)
    tmp = zeroconf.get_service_info(ZCNF_TYPE, ZCNF_NAME + '.' + ZCNF_TYPE)
    val_dict = zeroconf_Info2Values(tmp)

    act_assist = ActAssist(
        aiohttp_client.async_get_clientsession(hass),
        val_dict[KEY_HOSTNAME], 
        val_dict['port'],
        val_dict[KEY_WEBHOOK]
    )
    try:
        status = await act_assist.call_webhook()
        _LOGGER.warning('Webhook returned: ' + str(status))
        return status == 200
    except aiohttp.ClientError:
        _LOGGER.warning('No ')
        return False


config_entry_flow.register_discovery_flow(
    DOMAIN, "Activity Assistant", _async_has_devices, config_entries.CONN_CLASS_LOCAL_PUSH
)