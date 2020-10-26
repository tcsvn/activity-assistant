import unittest
from hassbrainapi.settings import *
from hassbrainapi.server import *
import hassbrainapi.util as hba_util

class ServerTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response)
        print(response)


    def test_put_rt_node(self):
        rt_node_id = 8
        print(SERVER_ADDRESS, USER, PASSWORD, rt_node_id)
        rt_node_url = hba_util.rt_node_id2rt_node_url(SERVER_ADDRESS, rt_node_id)
        print(rt_node_url)
        resp = put(SERVER_ADDRESS, USER, PASSWORD,
                   rt_node_url=rt_node_url + "/")
        print(resp)

    def test_put_rt_node_reset(self):
        rt_node_id = 8
        print(SERVER_ADDRESS, USER, PASSWORD, rt_node_id)
        rt_node_url = hba_util.rt_node_id2rt_node_url(SERVER_ADDRESS, rt_node_id)
        print(rt_node_url)
        resp = put(SERVER_ADDRESS, USER, PASSWORD,
                   rt_node_url=RESET_STRING)
        print(resp)

    def test_put_algorithm(self):
        HASSBRAIN_URL = "http://192.168.10.11:8000"
        HASSBRAIN_USER = "frontend"
        HASSBRAIN_PW = "asdf"
        algorithm_id = 2
        print(HASSBRAIN_URL, HASSBRAIN_USER, HASSBRAIN_PW, algorithm_id)
        hassbrainApi.server.put(
            HASSBRAIN_URL,
            HASSBRAIN_USER,
            HASSBRAIN_PW,
            algorithm_id=algorithm_id)

    def test_put_srv_address(self):
        HASSBRAIN_URL = "http://localhost:8000"
        HASSBRAIN_USER = "frontend"
        HASSBRAIN_PW = "asdf"
        srv_address = "asdf"
        print(HASSBRAIN_URL, HASSBRAIN_USER, HASSBRAIN_PW, srv_address)
        hassbrainApi.server.put(
            HASSBRAIN_URL,
            HASSBRAIN_USER,
            HASSBRAIN_PW,
            server_address=srv_address)

    def test_put(self):

        response = get(SERVER_ADDRESS,USER,PASSWORD)
        # temporary save values
        hass_address = response['hass_address']
        server_address = response['server_address']
        hass_api_token = response['hass_api_token']

        #1.  PUT
        print('-'*30)
        print('1 put:')
        response = put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            hass_address="test_hass",
            server_address=server_address,
            api_token=hass_api_token
        )
        putFailed = False
        self.assertEqual(response.status_code, 200)
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        print(response)

        if response['hass_address'] != "test_hass":
            putFailed = True
        print(str(putFailed))

        #2.  PUT
        print('-'*30)
        print('2 put:')
        response = put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            hass_address="test_hass2",
            server_address="test_server",
            api_token=hass_api_token
        )
        self.assertEqual(response.status_code, 200)
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        print(response)

        if response['hass_address'] != "test_hass2" \
                or response['server_address'] != "test_server":
            putFailed = True
        print(str(putFailed))

         #3.  PUT
        print('-'*30)
        print('3 put:')
        response = put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            server_address="test_server",
            api_token="test_token3"
        )
        self.assertEqual(response.status_code, 200)
        response = get(SERVER_ADDRESS,USER,PASSWORD)
        print(response)

        if response['hass_address'] != "test_hass2" \
                or response['server_address'] != "test_server"\
                or response['hass_api_token'] != "test_token3":
            putFailed = True
        print(str(putFailed))

        # put real values back
        response = put(
            url=SERVER_ADDRESS,
            user_name=USER,
            password=PASSWORD,
            server_address=server_address,
            hass_address=hass_address,
            api_token=hass_api_token
        )
        self.assertFalse(putFailed)

    def tearDown(self):
        pass

if __name__ == "__main__":
    unittest.main()