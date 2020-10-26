import unittest
import requests
from hassbrainapi.device import *
LOCATION_URL="/api/v1/devices/"
SERVER_ADDRESS="http://134.2.56.122:9000"
USER="admin"
PASSWORD="asdf"

class DeviceTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        self.assertIsNotNone(response)

    def test_create_put_delete(self):
        # CREATE
        name = "test_device"
        response = create(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            name=name,
            typ="binary_sensor",
            state="on"
        )
        print(response.json())
        id = response.json()['id']

    def test_put_1(self):
        #1.  PUT
        print('-'*30)
        print('1 put:')
        response = put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            id=id,
            name="test_device1",
            typ="asdf",
            state="off"
        )
        putFailed = False
        self.assertEqual(response.status_code, 200)
        id = response.json()['id']
        response = get_by_id(SERVER_ADDRESS,USER,PASSWORD, id)
        print(response)

        if response['name'] != "test_device1" \
                or response['typ'] != "asdf" \
                or response['state'] != "off":
            putFailed = True
        print(str(putFailed))


    def test_put_2(self):
        #2.  PUT
        print('-'*30)
        print('2 put:')
        response = put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            id=id,
            name="test_device2",
            typ="asdf2",
            location='reset',
            state='on'
        )

        self.assertEqual(response.status_code, 200)
        response = get_by_id(SERVER_ADDRESS,USER,PASSWORD, id)
        print(response)

        if response['name'] != "test_device2" \
                or response['location'] != None \
                or response['typ'] != "asdf2" \
                or response['state'] != 'on':
            putFailed = True
        print(str(putFailed))

    def test_delete_multi(self):
        # DELETE
        max = 500
        for id in range(100, max+1):
            delete(
                url=SERVER_ADDRESS,
                user_name=USER,
                password=PASSWORD,
                id=id
            )


    def test_delete(self):
        # DELETE
        id = 11
        delete(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            id=id
        )
        #response = requests.get(
        #    SERVER_ADDRESS + DEVICE_URL + "%s/"%(id),
        #    auth=(USER, PASSWORD)
        #).json()
        #self.assertEqual(response.status_code, 204)
        #self.assertEqual(response['detail'], "Not found.")

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()