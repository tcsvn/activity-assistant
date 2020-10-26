import unittest
import requests
from hassbrainApi.activity import *
SERVER_ADDRESS="http://localhost:8000"
USER="frontend"
PASSWORD="asdf"

class ActivityTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        self.assertIsNotNone(response)
        #print(response)
        id = response[0]['id']
        response = get_by_id(SERVER_ADDRESS, USER, PASSWORD, id)
        #print(response)
        self.assertIsNotNone(response)
        response = get_by_address(SERVER_ADDRESS + "/api/v1/activities/%s/"%(id),
                                  USER, PASSWORD)
        #print(response)
        self.assertIsNotNone(response)

    def test_create_put_delete(self):
        # CREATE
        name = "test_activity"
        create(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            name=name
        )
        response = requests.get(
            SERVER_ADDRESS + "/api/v1/activities/",
            auth=(USER, PASSWORD)
        ).json()


        # PUT
        id = 0
        id_found = False
        name2 = "test_activity2"
        for activity in response:
            if (activity['name'] == name):
                id_found = True
                id = activity['id']
        self.assertTrue(id_found)
        put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            id=id,
            name=name2
        )
        response = requests.get(
            SERVER_ADDRESS + "/api/v1/activities/%s/"%(id),
            auth=(USER, PASSWORD)
        ).json()
        self.assertTrue(response['name'] == name2)


        # DELETE
        delete(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            pk=id,
        )
        response = requests.get(
            SERVER_ADDRESS + "/api/v1/activities/%s/"%(id),
            auth=(USER, PASSWORD)
        ).json()
        self.assertEqual(response['detail'], "Not found.")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()