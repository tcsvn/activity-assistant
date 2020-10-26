import requests

def get(url, user_name, password):
    url = url + "/api/v1/smartphones/"
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + "/api/v1/smartphones/%s/"%(id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    return requests.get(url, auth=auth).json()

def delete(url, user_name, password, id):
    url += "/api/v1/smartphones/%s/"%(id)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)
