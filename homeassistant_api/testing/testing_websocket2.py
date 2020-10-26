import json
import unittest
import asyncio
import homeassistant_api.websocket2 as ws


"""
https://stackoverflow.com/questions/23033939/how-to-test-python-3-4-asyncio-code

decorator will block until 
the test method coroutine has finished
"""

HASS_ADDRESS = 'http://134.2.56.114:8123'
TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJkN2Q1ODZlODRmZTM0NGUyYTE0ZTc5ZTc2ODExZGE2MiIsImlhdCI6MTU1NDkxMzI3NSwiZXhwIjoxODcwMjczMjc1fQ.9aDP7bdxXqmRpndL4yV5B-65W2C0vgLziLskKEZ7fAA'

PERSON_0_NAME = "test0"
PERSON_0_USER_ID = 0
PERSON_1_NAME = "test1"
PERSON_1_USER_ID = 1
PERSON_2_NAME = "test2"
PERSON_2_USER_ID = 2
PERSON_CHRIS_NAME = "chris"
PERSON_CHRIS_USER_ID = 1

ACTIVITY_0 = "test_activity_0"
ACTIVITY_1 = "test_activity_1"
ACTIVITY_2 = "test_activity_2"

ACTIVITIES_0 = { ACTIVITY_0: 0.000,
                 ACTIVITY_1: 0.001,
                 ACTIVITY_2: 0.002}

DEVICE_0_NAME = "test0_name"
DEVICE_0_STATE_0 = "test0_state0"
DEVICE_0_STATE_1 = "test0_state1"
DEVICE_1_NAME = "test1_name"
DEVICE_1_STATE_0 = "test1_state0"
DEVICE_1_STATE_1 = "test1_state1"


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)
    return wrapper

class TestHassWebsocketClass(unittest.TestCase):
    def setUp(self):
        self.ws = ws.HassWs(HASS_ADDRESS, TOKEN)

    def tearDown(self):
        pass


    @async_test
    async def test_all(self):
        await self.ws.test_all()

    @async_test
    async def test_auth(self):
        await self.ws.connect()

    @async_test
    async def test_sub(self):
        await self.ws.connect()
        await self.ws.sub_events_state_changed()

    @async_test
    async def test_sub_unsub(self):
        await self.ws.connect()
        await self.ws.sub_events_state_changed()
        await asyncio.sleep(2)
        await self.ws.unsub_events_state_changed()

    @async_test
    async def test_listen_state_changed(self):
        await self.ws.connect()
        await self.ws.listen_states_changed(lambda x : print(str(x) + "\n"))


    @async_test
    async def test_fetch_states(self):
        await self.ws.connect()
        test = await self.ws.fetch_states()
        print(type(test))
        print(test)

    @async_test
    async def test_sub(self):
        await self.ws.connect()
        await asyncio.sleep(3)
        await self.ws.disconnect()


    @async_test
    async def test_listen_states_changed(self):
        """
        create an action in between the fetch states and the subscription
        to test if the ids work correctly
        :return:
        """
        await self.ws.connect()
        await self.ws.listen_states_changed(self.callback_test)

    async def callback_test(self, message):
        print('('*10)
        print(message)
        test = await self.ws.fetch_states()
        print(type(test))
        print(test)
        print('('*10)

class TestHassWebsocketClassPerson(unittest.TestCase):
    def setUp(self):
        self.ws = ws.HassWs(HASS_ADDRESS, TOKEN)

    def tearDown(self):
        pass

    @async_test
    async def test_person_list(self):
        await self.ws.connect()
        test = await self.ws.list_person()
        print(test)

    @async_test
    async def test_create_person(self):
        await self.ws.connect()

        test = await self.ws.create_person(
            #PERSON_CHRIS_NAME, PERSON_CHRIS_USER_ID)
            PERSON_0_NAME, PERSON_0_USER_ID)
            #PERSON_1_NAME, PERSON_1_USER_ID)
            #PERSON_2_NAME, PERSON_2_USER_ID)
            #'asdf', 29)
        print(test)

    @async_test
    async def test_update_person_act_0(self):
        await self.ws.connect()
        test = await self.ws.update_person(
            PERSON_0_NAME, PERSON_0_USER_ID, ACTIVITY_0)
            #PERSON_1_NAME, PERSON_1_USER_ID, ACTIVITY_0)
            #PERSON_2_NAME, PERSON_2_USER_ID, ACTIVITY_0)
        print(test)

    @async_test
    async def test_update_person_act_1(self):
        await self.ws.connect()
        test = await self.ws.update_person(
            PERSON_0_NAME, PERSON_0_USER_ID, ACTIVITY_1)
        #PERSON_1_NAME, PERSON_1_USER_ID, ACTIVITY_0)
        #PERSON_2_NAME, PERSON_2_USER_ID, ACTIVITY_0)
        print(test)

    @async_test
    async def test_update_person_act_2(self):
        await self.ws.connect()
        test = await self.ws.update_person(
            PERSON_0_NAME, PERSON_0_USER_ID, ACTIVITY_2)
        #PERSON_1_NAME, PERSON_1_USER_ID, ACTIVITY_0)
        #PERSON_2_NAME, PERSON_2_USER_ID, ACTIVITY_0)
        print(test)

    @async_test
    async def test_update_person_activities(self):
        await self.ws.connect()
        test = await self.ws.update_person(
            PERSON_0_NAME, PERSON_0_USER_ID, ACTIVITY_0, ACTIVITIES_0)
        #PERSON_1_NAME, PERSON_1_USER_ID, ACTIVITY_0)
        #PERSON_2_NAME, PERSON_2_USER_ID, ACTIVITY_0)
        print(test)

    @async_test
    async def test_delete_person(self):
        await self.ws.connect()
        test = await self.ws.delete_person(1)
        #test = await self.ws.delete_person(PERSON_0_USER_ID)
        #test = await self.ws.delete_person(PERSON_1_USER_ID)
        #test = await self.ws.delete_person(PERSON_2_USER_ID)

class TestHassWebsocketClassHassbrainDevice(unittest.TestCase):
    def setUp(self):
        self.ws = ws.HassWs(HASS_ADDRESS, TOKEN)

    def tearDown(self):
        pass

    @async_test
    async def test_device_list(self):
        await self.ws.connect()
        test = await self.ws.list_devices()
        print(test)


    @async_test
    async def test_create_device_0(self):
        await self.ws.connect()
        test = await self.ws.create_device(
            DEVICE_0_NAME, DEVICE_0_STATE_0)
            #PERSON_1_NAME, PERSON_1_USER_ID)
            #PERSON_2_NAME, PERSON_2_USER_ID)
            #'asdf', 29)
        print(test)

    @async_test
    async def test_create_device_1(self):
        await self.ws.connect()
        test = await self.ws.create_device(
            DEVICE_1_NAME, DEVICE_1_STATE_1)
        #PERSON_1_NAME, PERSON_1_USER_ID)
        #PERSON_2_NAME, PERSON_2_USER_ID)
        #'asdf', 29)
        print(test)

    @async_test
    async def test_update_device(self):
        await self.ws.connect()
        test = await self.ws.update_device(
            DEVICE_0_NAME, DEVICE_0_STATE_1)
            #DEVICE_0_NAME, DEVICE_0_STATE_0)
        print(test)



    @async_test
    async def test_concurrent_device_update(self):
        await self.ws.connect()

        try:
            await asyncio.gather(
                asyncio.create_task(self.ws.update_device(
                    #DEVICE_0_NAME, DEVICE_0_STATE_0)),
                    DEVICE_0_NAME, DEVICE_0_STATE_1)),
                asyncio.create_task(self.ws.update_device(
                    DEVICE_1_NAME, DEVICE_1_STATE_0)),
                    #DEVICE_1_NAME, DEVICE_1_STATE_1))
                asyncio.create_task(self.ws.update_device(
                    #DEVICE_0_NAME, DEVICE_0_STATE_0)),
                    DEVICE_0_NAME, DEVICE_0_STATE_1)),
                asyncio.create_task(self.ws.update_device(
                    DEVICE_1_NAME, DEVICE_1_STATE_0)),
                    #DEVICE_1_NAME, DEVICE_1_STATE_1))
                asyncio.create_task(self.ws.update_device(
                    #DEVICE_0_NAME, DEVICE_0_STATE_0)),
                    DEVICE_0_NAME, DEVICE_0_STATE_1)),
                asyncio.create_task(self.ws.update_device(
                    DEVICE_1_NAME, DEVICE_1_STATE_0)),
                    #DEVICE_1_NAME, DEVICE_1_STATE_1))
                asyncio.create_task(self.ws.update_device(
                    #DEVICE_0_NAME, DEVICE_0_STATE_0)),
                    DEVICE_0_NAME, DEVICE_0_STATE_1)),
                asyncio.create_task(self.ws.update_device(
                    DEVICE_1_NAME, DEVICE_1_STATE_0))
            )
        except TimeoutError:
            print('blabla'*1000)

    @async_test
    async def test_concurrent_devicelist_update(self):
        await self.ws.connect()
        tasks = []
        tasks.append(asyncio.create_task(self.ws.update_device(
                    DEVICE_0_NAME, DEVICE_0_STATE_0)),
                    #DEVICE_0_NAME, DEVICE_0_STATE_1))
        )
        tasks.append(
                asyncio.create_task(self.ws.update_device(
                    #DEVICE_1_NAME, DEVICE_1_STATE_0))
                    DEVICE_1_NAME, DEVICE_1_STATE_1))
        )
        print(tasks)
        try:
            res = await asyncio.gather(*tasks,
                    asyncio.create_task(self.ws.update_device(
                        #DEVICE_1_NAME, DEVICE_1_STATE_0))
                        DEVICE_1_NAME, DEVICE_1_STATE_1))
            )
            print(res)
        except TimeoutError:
            print('blabla'*1000)

    @async_test
    async def test_delete_device(self):
        await self.ws.connect()
        test = await self.ws.delete_device(
            DEVICE_0_NAME)
        print(test)



