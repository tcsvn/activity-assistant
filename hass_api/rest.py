import requests
import logging
from web.act_assist import settings

from web.frontend.util import get_server
"""
Implements an interface for https://developers.home-assistant.io/docs/api/rest
"""
logger = logging.getLogger(__name__)



def get(url: str, token: str) -> dict:
    headers = {
        'Authorization': f"Bearer {token}",
        'content-type': 'application/json',
    }
    req = requests.get(url, headers=headers)
    try:
        return req.json()
    except:
        return req


def get_errors(url, token):
    return get(url + "/api/error/all", token)


def get_states(url, token, name):
    url = url + "/api/states"
    resp = get(url, token)
    sens_list = []
    for item in resp:
        if name in item['entity_id']:
            sens_list.append(item)
    return sens_list

def get_config_folder(url, token):
    url = url + "/api/config"
    resp = get(url, token)
    return resp['config_dir']

def get_time_zone(url, token):
    return get(url + '/config', token)['time_zone']
    


def get_device_list(url: str, token: str) -> list:
    """ Return a list of entity ids for each device
    """
    devs = get(url + '/states', token)
    return [e['entity_id'] for e in devs]


def get_binary_sensors(url, token):
    sens_list = get_states(url, token, 'binary_sensor')
    res_dict = []
    for item in sens_list:
        res_dict.append({
            "name": item['entity_id'][14:],
            "typ": "binary_sensor"
            })
    return res_dict

def get_devices(url, token, filter_by_lst=None, filter_by_comp=None):
    """ queries the hass api for devices
    Parameters
    ----------
    filter_by_lst : list
    filter_by_comp : str

    """
    assert filter_by_lst is None or filter_by_comp is None

    res = []
    for dev in get(url + '/states', token):
        if filter_by_comp is not None:
            comp, _ = dev['entity_id'].split(".")
            if comp == filter_by_comp:
                res.append(dev)
            continue
        if filter_by_lst is not None:
            if dev['entity_id'] in filter_by_lst:
                res.append(dev)
            continue
        res.append(dev['entity_id'])
    return res

def get_user_names(url: str, token: str) -> list:
    """ Get all persons from homeassistant
    """
    entities = get_devices(url, token, filter_by_comp='person')
    return [ent['entity_id'] for ent in entities]



def get_filtered_devices(url, token, device_list):
    """

    :param url:
    :param token:
    :param device_list:
        a list of names of components in homeassistant
        example: ['binary_sensor', 'light', ... ]
    :return:
    """

    url = url + "/states"
    resp = get(url, token)
    res_dict_lst = []
    for item in resp:
        name, dev = item['entity_id'].split(".")
        if name in device_list and name != 'hassbrain':
            """
            hassbrain creates binary sensors that are updated
            from rt_node, therefore don't include those sensors
            """
            res_dict_lst.append(
                {
                    'name' : dev,
                    'component' : name
                }
            )
    return res_dict_lst


def get_state(url, token, entity_id):
    url = url + "/states/" + entity_id
    resp = get(url, token)
    return resp['state']

"""
Object oriented interfaces for the rest and the supervisor api
"""

class HASup():
    def __init__(self):
        srv = get_server()
        self.token = srv.hass_api_token
        self.url = settings.HASS_SUP_URL
    
    def get(self, url_suffix: str ) -> dict:
        url = self.url + url_suffix
        return get(url, self.token)

    def get_interface_ip(self, nr: int=0) -> str:
        """ Returns the ip address in the format 'xxx.xxx.xxx.xxx' of
            selected interface.
        """
        res = self.get('/network/info')
        res = res['data']['interfaces']
        if res:
            return res[0]['ipv4']['ip_address']


class HARest():
    def __init__(self):
        srv = get_server()
        self.token = str(srv.hass_api_token)
        self.url = settings.HASS_API_URL

    def get(self, url_suffix: str) -> dict: 
        url = self.url + url_suffix
        return get(url, self.token)

    def get_state(self, entity_id):
        return get_state(self.url, self.token, entity_id)


    def get_time_zone(self):
        return get_time_zone(self.url, self.token)

    def get_device_list(self):
        return get_device_list(self.url, self.token)
    
    def get_user_names(self):
        return get_user_names(self.url, self.token)

    def device_exists(self, entity_id):
        devices = get_device_list(self.url, self.token)
        return entity_id in devices

    def populate_input_selects(self, entity_id: str, options: list):
        headers = {
            'Authorization': f"Bearer {self.token}",
        }
        url = self.url + '/services/input_select/set_options'
        data = {'entity_id': entity_id, 'options': options}
        req = requests.post(url=url, json=data, headers=headers)
        return req

    def turn_off_input_boolean(self, entity_id: str):
        headers = {
            'Authorization': f"Bearer {self.token}",
        }
        url = self.url + '/services/input_boolean/turn_off'
        data = {'entity_id': entity_id}
        req = requests.post(url=url, json=data, headers=headers)
        return req

    def get_dev_area_mapping(self, devices: list, only_matches=False) -> list:
        """ Fetch areas for each device  

        Note the HA api does not allow for fetching areas but a template
        can be rendered https://www.home-assistant.io/docs/configuration/templating/
        with area in it
        
        """
        headers = {
            'Authorization': f"Bearer {self.token}",
            'content-type': 'application/json',
        }
        mapping = dict()
        for dev in devices:
            template = "{{ area_name('%s') }}"%(dev)

            url = self.url + '/template'
            data = {'template': template}
            req = requests.post(url=url, json=data, headers=headers)
            area = req.content.decode("utf-8")
            area = area if not area == 'None' else None

            if (not only_matches and area is None) or area is not None:
                mapping[dev] = area

        return mapping
