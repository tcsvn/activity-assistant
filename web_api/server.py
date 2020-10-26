import requests

API_URL = "/api/v1"
SERVER_URL = "/api/v1/server/1/"
RESET_STRING="reset"

def get(url, user_name, password):
    url = url + SERVER_URL
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def put(url, user_name, password,
        hass_address=None,
        server_address=None,
        api_token=None,
        algorithm_id=None,
        rt_node_url=None
        ):
    data = {}
    # reset the address with "reset"
    # otherwise it is a string or with None nothing changes
    # serveraddress and api_token analog
    if hass_address == RESET_STRING:
        data["hass_address"] = None
    elif hass_address != None:
        data["hass_address"] = hass_address

    if server_address == RESET_STRING:
        data["server_address"] = None
    elif server_address != None:
        data["server_address"] = server_address

    if api_token == RESET_STRING:
        data["hass_api_token"] = None
    elif api_token != None:
        data["hass_api_token"] = api_token

    if algorithm_id == RESET_STRING:
        data["selected_algorithm"] = None
    elif algorithm_id != None:
        api_url = url + API_URL
        data["selected_algorithm"] = api_url + "/algorithms/%s/"%(algorithm_id)

    if rt_node_url == RESET_STRING:
        data["realtime_node"] = None
    elif rt_node_url != None:
        data["realtime_node"] = rt_node_url

    server_url = url + SERVER_URL
    auth=(user_name, password)
    #print(data)
    req = requests.put(server_url, json=data, auth=auth)
    return req
