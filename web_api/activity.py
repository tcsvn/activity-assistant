import requests
ACTIVITY_URL = "/api/v1/activities/"

def get(url, user_name, password):
    url = url + ACTIVITY_URL
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + ACTIVITY_URL + "%s/"%(id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def create(url, user_name, password, name):
    url += ACTIVITY_URL
    data =  {"name" : name }
    auth=(user_name, password)
    return requests.post(url, json=data, auth=auth)

def delete(url, user_name, password, pk):
    url += ACTIVITY_URL + "%s/"%(pk)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)

def put(url, user_name, password,
        id,
        name
        ):
    url += ACTIVITY_URL + "%s/"%(id)
    data = {"name" : name}
    auth=(user_name, password)
    return requests.put(url, json=data, auth=auth)

