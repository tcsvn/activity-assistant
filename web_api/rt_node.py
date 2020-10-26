import json
import os
import requests
from hassbrainapi.settings import *
import hassbrainapi.util as hb_util
from io import BytesIO



def get(url, user_name, password):
    auth=(user_name, password)
    url = url + URL_RT_NODE
    print(url)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + URL_RT_NODE + "%s/" % (id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def create(url, user_name, password, name):
    url += URL_RT_NODE
    data =  {"name" : name }
    auth=(user_name, password)
    return requests.post(url, json=data, auth=auth)

def delete(url, user_name, password, pk):
    url += URL_RT_NODE + "%s/" % (pk)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)

def put(url, user_name, password, obs_pred=None):
    data = get(url, user_name, password)[0]
    rtn_id = data['id']

    data = {}
    if obs_pred == RESET_STRING:
        data["obs_pred"] = None
    elif obs_pred != None:
        data["obs_pred"] = obs_pred

    # debugj k
    url += URL_RT_NODE + "%s/" %(rtn_id)
    auth=(user_name, password)
    print(data)
    print(url)
    return requests.put(url, json=data, auth=auth)