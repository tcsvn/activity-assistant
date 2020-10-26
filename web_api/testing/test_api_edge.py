import unittest
import requests
from hassbrainApi.edge import *
EDGE_URL= "/api/v1/edges/"
SERVER_ADDRESS="http://localhost:8000"
USER="frontend"
PASSWORD="asdf"

class ActivityTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        self.assertIsNotNone(response)
        print(response)
        id = response[0]['id']
        response = get_by_id(SERVER_ADDRESS, USER, PASSWORD, id)
        print(response)
        self.assertIsNotNone(response)
        try:
            self.assertNotEqual(response['detail'], "Not found.")
        except:
            pass
        response = get_by_address(SERVER_ADDRESS + EDGE_URL + "%s/" % (id),
                                  USER, PASSWORD)
        print(response)
        try:
            self.assertNotEqual(response['detail'], "Not found.")
        except:
            pass
        self.assertIsNotNone(response)

    def test_create_put_delete(self):
        # CREATE
        source_id = "62"
        sink_id = "64"
        response = create(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            source_id=source_id,
            sink_id=sink_id)
        print(response)
        response = requests.get(
            SERVER_ADDRESS + EDGE_URL,
            auth=(USER, PASSWORD)
        ).json()
        id = 0
        id_found = False
        for edge in response:
            if (edge['source'] == "http://localhost:8000/api/v1/locations/%s/"%(source_id),
                edge['sink'] == "http://localhost:8000/api/v1/locations/%s/"%(sink_id)):
                id_found = True
                id = edge['id']
        self.assertTrue(id_found)

        # DELETE
        print("delete: " + str(id))
        delete(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            pk=id,
        )
        response = requests.get(
            SERVER_ADDRESS + EDGE_URL + "%s/" % (id),
            auth=(USER, PASSWORD)
        ).json()
        self.assertEqual(response['detail'], "Not found.")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()