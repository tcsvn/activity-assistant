import requests


def get(url, token):
    headers = {
        'Authorization': "Bearer " + token,
        'content-type': 'application/json',
    }
    req = requests.get(url, headers=headers)
    return req.json()


def get_errors(url, token):
    get(url + "/api/error/all", token)


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



def get_binary_sensors(url, token):
    sens_list = get_states(url, token, 'binary_sensor')
    res_dict = []
    for item in sens_list:
        res_dict.append({
            "name": item['entity_id'][14:],
            "typ": "binary_sensor"
            })
    return res_dict

def get_filtered_devices(url, token, device_list):
    """

    :param url:
    :param token:
    :param device_list:
        a list of names of components in homeassistant
        example: ['binary_sensor', 'light', ... ]
    :return:
    """

    url = url + "/api/states"
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
