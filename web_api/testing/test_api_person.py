import unittest
import requests
from hassbrainapi.person import *
from hassbrainapi.settings import *

PERSON_0_ID = "1"
PERSON_0_NAME = "test_person0"
PERSON_0_PRED_F = False
PERSON_0_PRED_T = True

class PersonTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        try:
            if (response['detail'] == "Not found"):
                return
        except:
            pass
        self.assertIsNotNone(response)
        print(response)

    def test_get_by_id(self):
        response = get_by_id(SERVER_ADDRESS, USER, PASSWORD,
                             PERSON_0_ID)
        try:
            if (response['detail'] == "Not found"):
                return
        except:
            pass
        self.assertIsNotNone(response)
        print(response)

    def test_get_by_address(self):
        TEST_PER_URL ='http://134.2.56.105:8000/api/v1/persons/1/'
        response = get_by_address(TEST_PER_URL, USER, PASSWORD)
        try:
            if (response['detail'] == "Not found"):
                return
        except:
            pass
        self.assertIsNotNone(response)
        print(response)

    def test_create(self):
        # CREATE
        name = PERSON_0_NAME
        response = create(
            SERVER_ADDRESS,
            USER,
            PASSWORD,
            name)

        print(response.reason)
        print(response.content)
        self.assertEqual(response.status_code, 201)
        #response = requests.get(
        #    SERVER_ADDRESS + URL_PERSON,
        #    auth=(USER, PASSWORD)
        #).json()
        #id_found = False
        #for person in response:
        #    if (person['name'] == name):
        #        id_found = True
        #self.assertTrue(id_found)

    def test_put_prediction(self):
        response = put(SERVER_ADDRESS, USER, PASSWORD,
                       PERSON_0_ID,
            prediction=PERSON_0_PRED_F
            #prediction=PERSON_0_PRED_T
        )
        print(response.content)

    def test_delete(self):
        response = delete(url=SERVER_ADDRESS, user_name=USER, password=PASSWORD,
            ide=PERSON_0_ID
        )
        print(response.text)
        print(response.content)
        #response = requests.get(
        #    SERVER_ADDRESS + LOCATION_URL + "%s/"%(id),
        #    auth=(USER, PASSWORD)
        #).json()
        #self.assertEqual(response['detail'], "Not found.")

    def tearDown(self):
        # Objekte können gelöscht oder geändert werden
        # in diesem Fall macht es jedoch wenig Sinn:
        print ("tearDown executed!")

if __name__ == "__main__":
    unittest.main()