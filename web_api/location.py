import requests
LOCATION_URL="/api/v1/locations/"

def get(url, user_name, password):
    url = url + LOCATION_URL
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + LOCATION_URL + "%s/"%(id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def create(url, user_name, password,
           name=None,
           x=0,
           y=0,
           loc_id=None):
    url += LOCATION_URL
    data =  {
        "name" : name,
        "x" : int(x),
        "y" : int(y),
        "node_id" : loc_id
    }
    auth=(user_name, password)
    return requests.post(url, json=data, auth=auth)

def delete(url, user_name, password, pk):
    url += LOCATION_URL + "%s/"%(pk)
    auth=(user_name, password)
    print(url)
    return requests.delete(url,auth=auth)

#def put(url, user_name, password,
#        id,
#        name
#        ):
#    url += LOCATION_URL + "%s/"%(id)
#    data = {"name" : name}
#    auth=(user_name, password)
#    return requests.put(url, json=data, auth=auth)

