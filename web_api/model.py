import json
import os
import requests
from hassbrainapi.settings import *
import hassbrainapi.util as hb_util
from io import BytesIO

# FIELDS
ALGORITHM = "algorithm"
PERSON = "person"
DATASET = "dataset"
FILE = "file"
BENCHMARK = "benchmark"

def get(server_url, user_name, password):
    auth=(user_name, password)
    server_url = server_url + URL_MODEL
    response = requests.get(server_url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + URL_MODEL + "%s/" % (id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(model_url, user_name, password):
    """

    :param model_url:
    :param user_name:
    :param password:
    :return:
    """
    auth=(user_name, password)
    response = requests.get(model_url, auth=auth).json()
    return response

def create(url, user_name, password, person_url, activity_url, score):
    url += URL_ACTIVITY_PRED
    data = {}

    data[PREDICTED_ACTIVITY] = activity_url
    data[PERSON] = person_url
    data[SCORE] = score
    auth=(user_name, password)
    print(data)
    return requests.post(url, json=data, auth=auth)

def create_with_ids(url, user_name, password, person_id, activity_id, score):
    data = {}

    data[PREDICTED_ACTIVITY] = url + URL_ACTIVITY + str(activity_id) + "/"
    data[PERSON] = url + URL_PERSON + str(person_id) + "/"
    data[SCORE] = score
    url += URL_ACTIVITY_PRED
    auth=(user_name, password)
    print(data)
    return requests.post(url, json=data, auth=auth)

def delete_by_id(url, user_name, password, ide):
    url += URL_ACTIVITY_PRED + "%s/" % (ide)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)

def put(url, user_name, password, ide, score):
    url += URL_ACTIVITY_PRED + "%s/" %(ide)
    data = {}
    data[SCORE] = score
    auth=(user_name, password)
    return requests.put(url, json=data, auth=auth)


from io import BytesIO

def download_model(url):
    """
    gets an url to the file, downloads it and returns a byte container
    :param url:
    :return:
    """
    url = hb_util.correct_url(url)
    resp = requests.get(url)
    return BytesIO(resp.content)
