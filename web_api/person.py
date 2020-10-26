import requests
from hassbrainapi.settings import *

FIELD_NAME = "name"
FIELD_PREDICTION = "prediction"
FIELD_SMARTPHONE = "smartphone"
FIELD_PRED_LOC = "predicted_location"
FIELD_PRED_ACT = "predicted_activities"
FIELD_SYN_ACT = "synthetic_activities"


def get(url, user_name, password):
    url = url + URL_PERSON
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_address(url, user_name, password):
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def get_by_id(url, user_name, password, id):
    url = url + URL_PERSON + "%s/"%(id)
    auth=(user_name, password)
    response = requests.get(url, auth=auth).json()
    return response

def create(url, user_name, password, name, activity_id=None, location_id=None):
    url_person = url + URL_PERSON
    if activity_id != None:
        activity_id = URL_ACTIVITY + "%s/"%(activity_id)
    if location_id != None:
        location_id = URL_LOCATION + "%s/"%(location_id)
    data = {}
    data[FIELD_NAME] = name
    data[FIELD_PREDICTION] = False
    data[FIELD_SMARTPHONE] = None
    data[FIELD_PRED_LOC] = location_id
    data[FIELD_PRED_ACT] = []

    print(data)
    auth=(user_name, password)
    return requests.post(url_person, json=data, auth=auth)

def delete(url, user_name, password,
           ide):
    url += URL_PERSON + "%s/"%(ide)
    auth=(user_name, password)
    return requests.delete(url,auth=auth)

def put(url, user_name, password,
        id,
        name=None,
        prediction=None,
        smartphone=None,
        predicted_activity_id=None,
        predicted_location_id=None
        ):
    data = {}
    if name is not None:
        data[FIELD_NAME] = name

    if prediction is not None:
        data[FIELD_PREDICTION] = prediction
    elif prediction == RESET_STRING:
        data[FIELD_PREDICTION] = False

    if predicted_location_id is not None:
        data[FIELD_PRED_LOC] = URL_LOCATION + "%s/"%(predicted_location_id)
        data[FIELD_PREDICTION] = True

    temp_per_dict = get_by_id(url, user_name, password, id)
    if smartphone is not None:
        data[FIELD_SMARTPHONE] = smartphone
    else:
        """
        get the person and extract the url of the smartphone or none
        """
        # todo check why "blank = True' is not working as expected
        smartphone_url = temp_per_dict[FIELD_SMARTPHONE]
        data[FIELD_SMARTPHONE] = smartphone_url

    # todo check why "blank = True' is not working as expected
    predicted_activities = temp_per_dict[FIELD_PRED_ACT]
    data[FIELD_PRED_ACT] = predicted_activities

    synthetic_activities = temp_per_dict[FIELD_SYN_ACT]
    data[FIELD_SYN_ACT] = synthetic_activities

    url += URL_PERSON + "%s/"%(id)
    auth=(user_name, password)
    return requests.put(url, json=data, auth=auth)
