import asyncio
import re
from enum import Enum

import websockets
import json
import traceback
import sys

def change_http2ws(url):
    url = url[4:]
    url = 'ws' + url
    return url

async def connect(url, token):
    url = url + "/api/websocket"
    url = change_http2ws(url)
    async with websockets.client.connect(url) as websocket:
        while True:
            message = await websocket.recv()
            if message is None:
                break
            message = json.loads(message)

            if message["type"] == "auth_required":
                print("sending auth...")
                await websocket.send(json.dumps({
                    "type": "auth",
                    "access_token": token
                }))

            if message["type"] == "auth_invalid":
                print("auth invalid")
                print("closing websocket...")
                websocket.close(status=1003, reason="auth is invalied")
                return None

            if message["type"] == "auth_ok":
                print('succesfull authenticated')
                return websocket


async def _send(websocket, payload):
    """
    sends the payload to the websocket connection, waits and returns the
    result of the message
    :param websocket:
    :param payload:
    :return:
        the result of the message
    """
    # todo if someone has a subscription and fetches states
    pong_waiter = await websocket.ping()
    await pong_waiter
    ide = json.loads(payload)['id']
    try:
        await websocket.send(payload)
    except Exception as e:
        pass
        #print(e)

    while True:
        message = None
        try:
            message = await websocket.recv()
            print('_'*10)
            print('msg: ', message)
        except Exception as e:
            print(e)
            print(message)
        if message is None:
            break
        message = json.loads(message)
        if message['id'] != ide:
            continue
        try:
            if message["success"]:
                return message["result"]
        except:
            traceback.print_exc(file=sys.stdout)
            print("_send : " + str(message))
            return

def gen_payload(ide, rest_dict):
    pl_dict = {}
    pl_dict['id'] = ide
    for key, item in rest_dict.items():
        pl_dict[key] = item

    return json.dumps(pl_dict)


async def subscribe_events(websocket, ide):
    await websocket.send(json.dumps({
        'id': ide,
        'type': 'subscribe_events',
        'event_type': 'state_changed'
    }))
    while True:
        message = await websocket.recv()
        if message is None:
            break
        message = json.loads(message)
        if message["success"] and message["type"] == "result":
            return True

async def listen_for_events(websocket, ide, callback_method):
    try:
        while True:
            message = await websocket.recv()
            #print("message: ", message)
            #print("message type: ", type(message))
            if message is None:
                break
            message = json.loads(message)
            #if message['id'] != ide:
            #    continue
            await callback_method(message)
    finally:
        await unsubscribe_events(websocket, ide)


async def unsubscribe_events(websocket, sub_id):
    await websocket.send(json.dumps({
        'id': sub_id+1,
        'type': 'unsubscribe_events',
        'subscription': sub_id
    }))
    while True:
        message = await websocket.recv()
        if message is None:
            break
        message = json.loads(message)
        #print('~'*10)
        #print(message)
        if message["success"] and message["type"] == "result":
            return True


# returns a list of states
async def fetch_states(websocket, ide):
    payload = json.dumps({
        "id": ide,
        "type": "get_states"
    })
    return await _send(websocket, payload)


async def fetch_config(websocket, ide):
    payload = json.dumps({
        "id": ide,
        "type": "get_config"
    })
    return await _send(websocket, payload)


async def fetch_services(websocket, ide):
    payload = json.dumps({
        "id": ide,
        "type": "get_services"
    })
    return await _send(websocket, payload)


# ------------ call services -------------------------------------
async def call_service(websocket, ide):
    domain = "light"
    service_name = "turn_on"
    payload = json.dumps({
        "id": ide,
        "type": "call_service",
        "domain": domain,
        "service": service_name,
        "service_data": {}
    })
    await _send(websocket, payload)


async def list_person(websocket, ide):
    """

    :param websocket:
    :param ide:
    :return:
        a dictionary containing
        'storage' : { persons in storage }
        'config' : {persons in config }
    """
    payload = json.dumps({
        "id" : ide,
        "type": "person/list"
    })
    return await _send(websocket, payload)


async def create_person(websocket, ide, name, user_id=None):
    """
    :param websocket:
    :param ide:
    :param name:
    :param user_id:
        if user_id is not given homeassistant creates a hexadecimal user_id
    :return:
    """
    payload = {
        "id" : ide,
        "type": "person/create",
        "name": name
    }
    if user_id is not None:
        payload["user_id"] = str(user_id)
    else:
        payload["user_id"] = None

    payload = json.dumps(payload)
    return await _send(websocket, payload)


async def update_person(websocket, ide, person_id, name, user_id, activity):
    payload = json.dumps({
        "id" : ide,
        "type": "person/update",
        "person_id": str(person_id),
        "name": name,
        "user_id": str(user_id),
        "activity": activity
    })
    return await _send(websocket, payload)

async def update_person_2(websocket, ide, person_id, name, user_id, activity, activities):
    payload = json.dumps({
        "id" : ide,
        "type": "person/update",
        "person_id": str(person_id),
        "name": name,
        "user_id": str(user_id),
        "activity": activity,
        "activities": activities
    })
    return await _send(websocket, payload)

async def delete_person(websocket, ide, person_id):
    """

    :param websocket:
    :param ide:
    :param person_id:
        is the internal hex code identifieing the person
        don't confuse with user_id
    :return:
    """
    payload = json.dumps({
    #payload = gen_payload(ide,{
        "id": ide,
        "type": "person/delete",
        "person_id": str(person_id)
    })
    return await _send(websocket, payload)


async def create_hassbrain_device(websocket, ide, name, state):
    payload = json.dumps({
        "id": ide,
        "type": "hassbrain/device/create",
        "name": name,
        "state": state
    })
    return await _send(websocket, payload)

async def update_hassbrain_device(websocket, ide, name, state):
    payload = json.dumps({
        "id": ide,
        "type": "hassbrain/device/update",
        "name": name,
        "state": state
    })
    return await _send(websocket, payload)

async def delete_hassbrain_device(websocket, ide, name):
    payload = json.dumps({
        "id": ide,
        "type": "hassbrain/device/delete",
        "name": name
    })
    return await _send(websocket, payload)


async def list_devices(websocket, ide):
    """

    :param websocket:
    :param ide:
    :return:
    """
    payload = json.dumps({
        "id" : ide,
        "type": "hassbrain/device/list"
    })
    res = await _send(websocket, payload)
    return res['device_list']


class WsState(Enum):
    INITIAL = 0
    TRYINGTOAUTH = 1
    AUTHENTICATED = 2

class HassWs(object):

    def __init__(self, url, token):
        self._state = WsState.INITIAL
        self._url = url
        self._token = token
        self._websocket = None
        self._event_sub_id = 10
        self._id_counter = 0
        self.callbacks = []

    async def connect(self):
        token = self._token
        url = self._url
        url = url + "/api/websocket"
        url = change_http2ws(url)
        async with websockets.client.connect(url) as websocket:
            async for message in websocket:
                await self.consumer(json.loads(message))

    async def authenticate(self):
        print("sending auth...")
        # todo enable
        #await websocket.send(json.dumps({
        #    "type": "auth",
        #    "access_token": token
        #}))

    def _is_authenticating(self, message):
        try:
            return message["type"] == "auth_required"
        except Exception as e:
            print(e)

    def _is_auth_valid(self, message):
        if message["type"] == "auth_ok":
            pass
        #if message["type"] == "auth_invalid":
        #    print("auth invalid")
        #    print("closing websocket...")
        #    websocket.close(status=1003, reason="auth is invalied")

    async def consumer(self, message):
        if self._state == WsState.INITIAL and self._is_authenticating(message):
            await self.authenticate()
            self._state = WsState.TRYINGTOAUTH
            return

        if self._state == WsState.TRYINGTOAUTH and self._is_auth_valid(message):
            self._state = WsState.AUTHENTICATED
            return

        if self._state == WsState.AUTHENTICATED:
            for callback in self.callbacks:
                callback(message)

    async def producer(self):
        print('lu')

    async def producer_handler(self, websocket, path):
        while True:
            message = await self.producer()
            await websocket.send(message)

    async def test_all(self):
        websocket = await self.conn()
        ide = self._id_counter + 3
        payload = json.dumps({
            "id" : ide,
            "type": "hassbrain/device/list"
        })
        #while True:
        await websocket.send(payload)

        async for message in websocket:
            print('went here')
            await self.consumer(message)

        #    msg = await websocket.recv()
        #    print(msg)

    async def disconnect(self):
        self._websocket.close()

    async def sub_events_state_changed(self):
        self._event_sub_id = self._id_counter
        self._id_counter += 1
        print('subscribing...')
        if await subscribe_events(self._websocket, self._event_sub_id):
            print('succesfully subscribed')
        else:
            print('an error account')

    async def unsub_events_state_changed(self):
        print('unsubscribing...')
        if await unsubscribe_events(self._websocket, self._event_sub_id):
            print('succesfully unsubscribed')
        else:
            print('an error account')
        self._id_counter += 2

    async def listen_states_changed(self, callback_method):
        await self.sub_events_state_changed()
        await listen_for_events(self._websocket, self._id_counter,
                                callback_method
        )


    async def fetch_states(self):
        self._id_counter += 1
        print('fetching states...')
        states = await fetch_states(self._websocket, self._id_counter)
        #print(states)
        return states

    async def call_service(self, domain, service):
        raise NotImplementedError

    async def list_person(self):
        self._id_counter += 1
        print('listing person...')
        return await list_person(self._websocket, self._id_counter)

    async def create_person(self, name, user_id):
        self._id_counter += 1
        print('creating person...')
        return await create_person(self._websocket, self._id_counter,
                                   name, user_id)

    async def update_person(self, name, user_id, activity, activities=None):
        self._id_counter += 1
        person_id = await self.user_id2person_id(user_id)
        print('update person...')
        # todo change to update also attributes
        if activities is None:
            return await update_person(
                websocket=self._websocket,
                ide=self._id_counter,
                person_id=person_id,
                name=name,
                user_id=user_id,
                activity=activity
            )
        else:
             return await update_person_2(
                websocket=self._websocket,
                ide=self._id_counter,
                person_id=person_id,
                name=name,
                user_id=user_id,
                activity=activity,
                activities=activities
            )

    async def delete_person(self, user_id):
        print('deleting person...')
        person_id = await self.user_id2person_id(user_id)
        #print('*'*100)
        #print(person_id)
        #print(user_id)
        #print('*'*100)
        self._id_counter += 1
        return await delete_person(self._websocket, self._id_counter, person_id)

    async def user_id2person_id(self, user_id):
        self._id_counter += 1
        listp = await list_person(self._websocket, self._id_counter)
        self._id_counter += 1
        person_id = self.list_person2person_id(user_id, listp)
        #print(person_id)
        return person_id

    def list_person2person_id(self, user_id, list_person):
        for person in list_person['storage']:
            #print(person)
            if not re.search('[a-zA-Z]', person['user_id']) \
                    and int(person['user_id']) == int(user_id):
                # all ids created from the websocket are integers, therefore
                # an id containing letters can't be a person we would want to delete
                return person['id']

    async def list_devices(self):
        self._id_counter += 1
        print('listing devices...')
        return await list_devices(self._websocket, self._id_counter)

    async def create_device(self, device_name, state):
        self._id_counter += 1
        return await create_hassbrain_device(
            self._websocket,
            self._id_counter,
            device_name,
            state)

    async def update_device(self, device_name, state):
        self._id_counter += 1
        return await update_hassbrain_device(
            self._websocket,
            self._id_counter,
            device_name,
            state
            )

    async def delete_device(self, device_name):
        self._id_counter += 1
        return await delete_hassbrain_device(
            self._websocket,
            self._id_counter,
            device_name)
