# most of the methods are borrowed from
# https://github.com/robmarkcole/HASS-data-detective/blob/master/detective/core.py

from . import config
from urllib.parse import urlparse

def url_from_hass_config(path, **kwargs):
    """ returns the type and url """
    url = config.db_url_from_hass_config(path)
    return url, urlparse(url).scheme.split("+")[0] 