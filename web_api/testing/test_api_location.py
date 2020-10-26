import unittest
import requests
from hassbrainApi.location import *
LOCATION_URL="/api/v1/locations/"
SERVER_ADDRESS="http://localhost:8000"
#USER="frontend"
USER="admin"
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
        try:
            self.assertNotEqual(response['detail'], "Not found.")
        except:
            pass
        response = get_by_address(SERVER_ADDRESS + LOCATION_URL + "%s/"%(id),
                                  USER, PASSWORD)
        #print(response)
        try:
            self.assertNotEqual(response['detail'], "Not found.")
        except:
            pass
        self.assertIsNotNone(response)

    def test_create(self):
        name = "test_location"
        response = create(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            name=name,
            x=500,
            y=500,
            loc_id=20
        )
        self.assertEqual(response.status_code, 201)

        id = response.json()['id']
        response = requests.get(
            SERVER_ADDRESS + LOCATION_URL,
            auth=(USER, PASSWORD)
        ).json()
        id_found = False
        for location in response:
            print(location)
            if (id == location['id']):
                id_found = True
        self.assertTrue(id_found)

    def test_delete(self):
        response = delete(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            pk=id,
        )
        self.assertEqual(response.status_code, 204)

        response = requests.get(
            SERVER_ADDRESS + LOCATION_URL + "%s/"%(id),
            auth=(USER, PASSWORD)
        ).json()
        self.assertEqual(response['detail'], "Not found.")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()