import json
import os
import requests
from hassbrainapi.device import RESET_STRING

import hassbrainapi.util as hb_util
from io import BytesIO

ALGORITHM_URL = "/api/v1/algorithms/"

def download_model(url):
    """
    gets an url to the file, downloads it and returns a byte container
    :param url:
    :return:
    """
    url = hb_util.correct_url(url)
    resp = requests.get(url)
    return BytesIO(resp.content)


def get(url, user_name, password):
    if not "api/v1/algorithms" in url:
        url = url + ALGORITHM_URL

    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + ALGORITHM_URL + "%s/" % (id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def create(url, user_name, password, name):
    url += ALGORITHM_URL
    data =  {"name" : name }
    auth=(user_name, password)
    return requests.post(url, json=data, auth=auth)

def delete(url, user_name, password, pk):
    url += ALGORITHM_URL + "%s/" % (pk)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)

def deselect_algorithm(url, user_name, password, id):
    data = {}
    data["model"] = None
    url += ALGORITHM_URL + "%s/"%(id)
    auth=(user_name, password)
    return requests.put(url, json=data, auth=auth)

def put(url, user_name, password,
        id,
        obs_pred=None
        ):
    data = {}
    if obs_pred == RESET_STRING:
        data["obs_pred"] = None
    elif obs_pred != None:
        data["obs_pred"] = obs_pred
    # debugj k
    data["name"] = "HMM"
    data["id"] = 2
    data["model"] = None
    data['description'] = 'asdf'
    data['multiple_person'] = False
    data['unsupervised'] = False
    data['activity_duration'] = False
    data['location'] = False
    data['train_dataset'] = False
    data['benchmark'] = None
    # debugj k

    url += ALGORITHM_URL + "%s/"%(id)
    auth=(user_name, password)
    print(data)
    print(url)
    return requests.put(url, json=data, auth=auth)


def put_model(url, user_name, password,
                id,
                model_file
                ):
    url += ALGORITHM_URL + "%s/" % (id)
    data = {"description" : "asdf"}
    auth=(user_name, password)
    return requests.put(url, files=model_file, auth=auth)
    #return requests.put(url, json=data, files=model_file, auth=auth)
    #return requests.put(url, json=data, auth=auth)

def put2(url, user_name, password,
        id,
        model_file,
        ):
    url += ALGORITHM_URL + "%s/" % (id)
    info = {"description" : "asdf"}
    auth_token=(user_name, password)
    data = {
        'token' : auth_token,
        'info'  : info,
    }
    headers = {'Content-type': 'multipart/form-data'}

    files = {'model': open('asdf.joblib', 'rb')}

    return requests.put(url, files=files, data=data, headers=headers)

def send_request(url, user_name, password,
        id,
        model_file,
        ):
    file = "asdf.joblib"
    payload = {"description": "asdf"}
    auth=(user_name, password)
    files = {
         'json': (None, json.dumps(payload), 'application/json'),
         'file': (os.path.basename(file), open(file, 'rb'), 'application/octet-stream')
    }

    r = requests.put(url, files=files, auth=auth)
    return r
