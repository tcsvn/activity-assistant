import requests
EDGE_URL= "/api/v1/edges/"
API_URL= "/api/v1/"

def get(url, user_name, password):
    url = url + EDGE_URL
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + EDGE_URL + "%s/" % (id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def create(url, user_name, password,
           source_id, sink_id):
    source_url = url + API_URL + "locations/" + str(source_id) + "/"
    sink_url = url + API_URL + "locations/" + str(sink_id) + "/"
    data = {
        "source": source_url,
        "sink" : sink_url,
        "distance" : 0
    }
    url += EDGE_URL
    auth=(user_name, password)
    return requests.post(url, json=data, auth=auth)

def delete(url, user_name, password, pk):
    url += EDGE_URL + "%s/" % (pk)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)
