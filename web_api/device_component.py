import json
import os
import requests
from hassbrainapi.settings import *
import hassbrainapi.util as hb_util
from io import BytesIO

# FIELDS

def get(url, user_name, password):
    auth=(user_name, password)
    url = url + URL_DEVICE_COMP
    print(url)
    response = requests.get(url, auth=auth).json()
    return response

#def get_by_id(url, user_name, password, id):
#    url = url + URL_DEVICE_PRED + "%s/" % (id)
#    auth=(user_name, password)
#    response = requests.get(url, auth=auth).json()
#    return response
#
#def get_by_address(url, user_name, password):
#    auth=(user_name, password)
#    response = requests.get(url, auth=auth).json()
#    return response
#
#def create(url, user_name, password, rt_node_url, device_url, score):
#    url += URL_DEVICE_PRED
#    data =  {}
#
#    data[PREDICTED_ACTIVITY] = device_url
#    data[SCORE] = score
#    data[RT_NODE] = rt_node_url
#    auth=(user_name, password)
#    print('~'*10)
#    print(url)
#    print(data)
#    print('~'*10)
#    return requests.post(url, json=data, auth=auth)
#
#def delete(url, user_name, password, ide):
#    url += URL_DEVICE_PRED + "%s/" % (ide)
#    auth=(user_name, password)
#    return requests.delete(url,auth=auth)
#
#def put(url, user_name, password, ide, score):
#    url += URL_DEVICE_PRED + "%s/" %(ide)
#    data = {}
#    data[SCORE] = score
#    auth=(user_name, password)
#    print(url)
#    print(data)
#    return requests.put(url, json=data, auth=auth)
