from homeassistant import config_entries
from homeassistant.helpers import config_entry_flow
from . import call_webhook

from .const import DOMAIN

async def _async_has_devices(hass) -> bool:
    """Return if there are devices that can be discovered."""
    # check if the api is reachable
    import requests
    tmp = requests.get('http://local-act-assist:8000/webhook')
    return tmp.status_code == 200


config_entry_flow.register_discovery_flow(
    DOMAIN, "Activity Assistant", _async_has_devices, config_entries.CONN_CLASS_LOCAL_PUSH
)