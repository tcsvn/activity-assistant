import unittest
import requests
import joblib
import hassbrainapi.util as hb_util
#SERVER_ADDRESS="http://192.168.10.11:8000"
SERVER_ADDRESS="http://134.2.56.118:8000"
USER="admin"
PASSWORD="asdf"

class TestFile(object):
    def __init__(self, num):
        self._num = num

class UtilTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_correct_url(self):
        url = "134.2.56.183:80089"
        crt_url = hb_util.correct_url(url)
        print(crt_url)

    def test_create_device_url(self):
        url = "134.2.56.183:80089"
        dev_url = hb_util.create_device_url(url, 3)
        print(dev_url)

if __name__ == "__main__":
    unittest.main()