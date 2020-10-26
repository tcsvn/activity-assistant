import unittest
from hassbrainapi.settings import *
from hassbrainapi.activity_prediction import *

ACT_0_ID = "2"
ACT_1_ID = "3"
PRED_ACT_0_ID = "0"
PRED_ACT_1_ID = "1"
PRED_ACT_2_ID = "2"
PER_0_ID = "1"

SCORE_0 = 0.923
SCORE_1 = 0.111
SCORE_2 = 0.222
SCORE_3 = 0.333

ACT_URL_0 = SERVER_ADDRESS + URL_ACTIVITY + ACT_0_ID + "/"
ACT_URL_1 = SERVER_ADDRESS + URL_ACTIVITY + ACT_1_ID + "/"

PERSON_URL_0 = SERVER_ADDRESS + URL_PERSON + PER_0_ID + "/"


class PersonTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_get(self):
        response = get(SERVER_ADDRESS, USER, PASSWORD)
        try:
            if (response['detail'] == "Not found"):
                return
        except:
            pass
        self.assertIsNotNone(response)
        print(response)

    def test_create(self):
        print(ACT_URL_0)
        resp = create(SERVER_ADDRESS, USER, PASSWORD,
                      person_url=PERSON_URL_0,
                      activity_url=ACT_URL_0,
                      score=SCORE_0)
        print(resp)
        print(resp.reason)

    def test_create_by_id(self):
        print(ACT_URL_0)
        resp = create_with_ids(SERVER_ADDRESS, USER, PASSWORD,
                      person_id=PER_0_ID,
                      activity_id=ACT_1_ID,
                      score=SCORE_1)
        print(resp)
        print(resp.reason)

    def test_put(self):
        response = put(SERVER_ADDRESS, USER, PASSWORD,
            PRED_ACT_1_ID, SCORE_0)
        print(response)

    def test_delete(self):
        resp = delete_by_id(SERVER_ADDRESS, USER, PASSWORD,
            PRED_ACT_0_ID)
        print(resp)

    def tearDown(self):
        # Objekte können gelöscht oder geändert werden
        # in diesem Fall macht es jedoch wenig Sinn:
        print ("tearDown executed!")

if __name__ == "__main__":
    unittest.main()