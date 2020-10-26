import json
import unittest
import asyncio
from hassbrain_rt_node.controller import Controller, CustomQueue

"""
https://stackoverflow.com/questions/23033939/how-to-test-python-3-4-asyncio-code

decorator will block until 
the test method coroutine has finished
"""

class TestQueue(unittest.TestCase):

    def setUp(self):
        self.queue = CustomQueue(10)

    def test_push(self):
        self.queue.push('1')
        print(self.queue.as_list())

    def test_push_remove(self):
        self.queue.push('1')
        self.queue.push('2')
        self.queue.push('3')
        print(self.queue.as_list())
        self.queue.remove_last_pushed()
        print(self.queue.as_list())

HB_ADDR = "http://134.2.56.122:8000"
HB_USER = "admin"
HB_PW = "asdf"


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper

class TestHassWebsocketClass(unittest.TestCase):
    def setUp(self):
        self.ctrl = Controller(HB_ADDR, HB_USER, HB_PW)

    def tearDown(self):
        pass


    #@async_test
    #async def test_init(self):
    #    print(self.ctrl)

    def test_init(self):
        print(self.ctrl)

    def test_run(self):
        self.ctrl.run()


    def test_update_devices_hassbrain(self):
        self.ctrl._hassbrain_update_preddevices()

    def test_delete_devices_hassbrain(self):
        self.ctrl._hassbrain_delete_preddevices()

    def test_create_devices_hassbrain(self):
        self.ctrl._hassbrain_create_preddevices(
            self.ctrl._dev_dict,
            self.ctrl._hb_dev_name_id_hashmap)

    def test_delete_act_hassbrain(self):
        self.ctrl._hassbrain_delete_predactivities()


    def test_create_act_hassbrain(self):
        self.ctrl._hassbrain_create_predactivities()
