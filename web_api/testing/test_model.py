import unittest
from hassbrainapi.settings import *
from hassbrainapi.model import *

MODEL_0_ID = "1"
MODEL_1_ID = "7"

MODEL_URL_0 = SERVER_ADDRESS + URL_MODEL + MODEL_0_ID + "/"
#DEVICE_URL_1 = SERVER_ADDRESS + URL_DEVICE + DEV_1_ID + "/"
#RT_NODE_URL_0 = SERVER_ADDRESS + URL_RT_NODE + RT_0_ID + "/"

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


    def test_get_by_address(self):
        response = get_by_address(MODEL_URL_0,USER,PASSWORD)
        try:
            if (response['detail'] == "Not found"):
                return
        except:
            pass
        self.assertIsNotNone(response)
        print(response)

#    def test_create(self):
#        print(DEVICE_URL_0)
#        resp = create(SERVER_ADDRESS, USER, PASSWORD,
#                      rt_node_url=RT_NODE_URL_0,
#                      device_url=DEVICE_URL_0,
#                      score=SCORE_0)
#        print(resp)
#        print(resp.reason)
#
#    def test_put(self):
#        response = put(SERVER_ADDRESS, USER, PASSWORD,
#            PRED_DEV_0_ID, SCORE_1)
#        print(response)
#        print(response.reason)
#
#    def test_delete(self):
#        resp = delete(SERVER_ADDRESS, USER, PASSWORD,
#            PRED_DEV_0_ID)
#        print(resp)

    def tearDown(self):
        # Objekte können gelöscht oder geändert werden
        # in diesem Fall macht es jedoch wenig Sinn:
        print ("tearDown executed!")

if __name__ == "__main__":
    unittest.main()