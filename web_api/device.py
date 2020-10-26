import requests
API_URL = "/api/v1"
LOCATION_URL="/api/v1/locations/"
DEVICE_URL = "/api/v1/devices/"
RESET_STRING="reset"

def get(url, user_name, password):
    url = url + DEVICE_URL
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response


def get_by_id(url, user_name, password, id):
    url = url + DEVICE_URL + "%s/"%(id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def put(url, user_name, password,
        id,
        name,
        typ,
        state,
        location=None
        ):
    data = {}
    if  name == RESET_STRING:
        data["name"] = None
    elif name != None:
        data["name"] = name

    if  location == RESET_STRING:
        data["location"] = None
    elif location != None:
        data["location"] = location

    if  typ == RESET_STRING:
        data["typ"] = None
    elif typ != None:
        data["typ"] = typ

    if  state == RESET_STRING:
        data["state"] = None
    elif state != None:
        data["state"] = state

    url += DEVICE_URL + "%s/"%(id)
    auth=(user_name, password)
    return requests.put(url, json=data, auth=auth)

def create(url, user_name, password,
                      name, typ, state):
    url = url + DEVICE_URL
    data =  {
            "name" : name,
            "location" : None,
            "typ" : typ,
            "state" : state
            }
    auth=(user_name, password)
    return requests.post(url, json=data, auth=auth)

def delete(url, user_name, password, id):
    url_device = url + DEVICE_URL + "%s/"%(id)
    auth=(user_name, password)
    return requests.delete(url_device, auth=auth)
