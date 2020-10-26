import json
import unittest
import asyncio
import homeassistant_api.rest as hass_rest

"""
https://stackoverflow.com/questions/23033939/how-to-test-python-3-4-asyncio-code

decorator will block until 
the test method coroutine has finished
"""

#HASS_ADDRESS = 'http://134.2.56.118:8123'
#HASS_ADDRESS = 'http://134.2.56.122:8123'
HASS_ADDRESS = 'http://134.2.56.112:8123'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkN2Q1ODZlODRmZTM0NGUyYTE0ZTc5ZTc2ODExZGE2MiIsImlhdCI6MTU1NDkxMzI3NSwiZXhwIjoxODcwMjczMjc1fQ.9aDP7bdxXqmRpndL4yV5B-65W2C0vgLziLskKEZ7fAA'

#PERSON_0_NAME = "test0"
#PERSON_0_USER_ID = 0
#PERSON_1_NAME = "test1"
#PERSON_1_USER_ID = 1
#PERSON_2_NAME = "test2"
#PERSON_2_USER_ID = 2
#PERSON_CHRIS_NAME = "chris"
#PERSON_CHRIS_USER_ID = 1
#
#ACTIVITY_0 = "test_activity_0"
#DEVICE_0_NAME = "test0_name"
#DEVICE_0_STATE_0 = "test0_state0"
#DEVICE_0_STATE_1 = "test0_state1"
#DEVICE_1_NAME = "test1_name"
#DEVICE_1_STATE_0 = "test1_state0"
#DEVICE_1_STATE_1 = "test1_state1"

# ----------------------------------------
DEVICE_TYP_BIN = 'binary_sensor'
DEVICE_TYP_LIGHT = 'light'
DEVICE_TYP_SWITCH = 'switch'

DEV_LIST_0 = [DEVICE_TYP_BIN]
DEV_LIST_1 = [DEVICE_TYP_BIN, DEVICE_TYP_LIGHT]
DEV_LIST_2 = [DEVICE_TYP_BIN, DEVICE_TYP_LIGHT, DEVICE_TYP_SWITCH]

class TestRest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_errors(self):
        resp = hass_rest.get_errors(HASS_ADDRESS, TOKEN)
        print(resp)

    def test_get_sensors(self):
        resp = hass_rest.get_states(HASS_ADDRESS, TOKEN, DEVICE_TYP_BIN)
        print('#'*100)
        print(resp)

    def test_get_filtered_devices_only_binary(self):
        resp = hass_rest.get_filtered_devices(HASS_ADDRESS, TOKEN,
             DEV_LIST_0
        )

    def test_get_filtered_devices(self):
        resp = hass_rest.get_filtered_devices(HASS_ADDRESS, TOKEN,
            DEV_LIST_2
        )
        self.print_list(resp)

    def test_get_config(self):
        print(HASS_ADDRESS)
        print(TOKEN)
        resp = hass_rest.get_config_folder(HASS_ADDRESS, TOKEN)
        print('#'*100)
        print(resp)


    def print_list(self, lst):
        for item in lst:
            print(item)
