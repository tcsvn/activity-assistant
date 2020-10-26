import unittest
from hassbrainapi.settings import *
from hassbrainapi.rt_node import *

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

    def test_put(self):
        obs_pred = "{asdf}"
        response = put(SERVER_ADDRESS, USER, PASSWORD, obs_pred)
        print(response)

    def test_create_put_delete(self):
        # CREATE
        name = "test_person"
        response = create(
            SERVER_ADDRESS,
            USER,
            PASSWORD,
            name)

        self.assertEqual(response.status_code, 201)

        response = requests.get(
            SERVER_ADDRESS + PERSON_URL,
            auth=(USER, PASSWORD)
        ).json()
        id_found = False
        for person in response:
            if (person['name'] == name):
                id_found = True
        self.assertTrue(id_found)

    def test_delete(self):
        # DELETE
        #delete(
        #    url=SERVER_ADDRESS,
        #    user_name=USER,
        #    password=PASSWORD,
        #    pk=id,
        #)
        #response = requests.get(
        #    SERVER_ADDRESS + LOCATION_URL + "%s/"%(id),
        #    auth=(USER, PASSWORD)
        #).json()
        #self.assertEqual(response['detail'], "Not found.")
        pass

    def tearDown(self):
        # Objekte können gelöscht oder geändert werden
        # in diesem Fall macht es jedoch wenig Sinn:
        print ("tearDown executed!")

if __name__ == "__main__":
    unittest.main()