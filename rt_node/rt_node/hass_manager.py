import asyncio

from homeassistant_api.websocket import HassWs

from hassbrain_rt_node.model_manager import ModelManager


class HomeassistantManager():

    def __init__(self, hass_ws : HassWs, initial_val, per_dict_list,sens_next_obs_name, round_fct):
        self._hass_ws = hass_ws
        self._url = hass_ws._url
        self._token = hass_ws._token

        self._initial_val = initial_val
        self._per_dict_list = per_dict_list
        self._sens_next_obs_name = sens_next_obs_name
        self._round_fct = round_fct

    async def connect_websocket(self):
        """
        checks if a connection is still active and
        closes the connection and reconnects a websocket
        :return:
        """
        print('reconnecting')
        if self._hass_ws.is_connected():
            await self._hass_ws.disconnect()
        await self._hass_ws.connect()

    async def disconnect_websocket(self):
        await self._hass_ws.disconnect()

    async def _get_hass_states(self, ws):
        self._hass_states = await ws.fetch_states()

    async def sync_hass_states(self):
        self._hass_states = await self._hass_ws.fetch_states()

    async def delete_all_hb_devices(self, new_ws):
        # first make shure no hassbrain device is left in home assistant
        hass_dev_list = await new_ws.list_devices()
        for dev_name in hass_dev_list:
            await new_ws.delete_device(dev_name)

    async def create_obs_dev(self, ws):
        # create sensor for next sampled device
        await ws.create_device(
            self._sens_next_obs_name,
            self._initial_val
        )

    async def create_all_hb_devices(self, ws, dev_dict):
            for device in dev_dict:
                # create device in home assistant
                hass_dev_name = ModelManager.dev_name2hb_dev_name(device)
                await ws.create_device(
                    hass_dev_name,
                    self._initial_val
                )
    async def get_hass_states(self):
        new_ws = HassWs(self._url, self._token)
        await new_ws.connect()
        hass_states = await new_ws.fetch_states()
        await new_ws.disconnect()
        return hass_states

    async def flush_homeassistant(self, dev_dict, create_dev=False):
        new_ws = HassWs(self._url, self._token)
        await new_ws.connect()
        await self.delete_all_hb_devices(new_ws)
        if create_dev:
            await self.create_all_hb_devices(new_ws, dev_dict)
            await self.create_obs_dev(new_ws)
            await self._get_hass_states(new_ws)
        await new_ws.disconnect()


    async def update_homeassistant(self, pred_act, pred_act_scores_dict, pred_dev, xnp1_dict):
        if xnp1_dict:
            hass_dev_tasks = self._create_devices_request_tasks(xnp1_dict)
        else:
            hass_dev_tasks = []
        if pred_act and pred_act_scores_dict:
            hass_per_tasks = self.create_person_request_tasks(pred_act, pred_act_scores_dict)
        else:
            hass_per_tasks = []
        if pred_dev:
            hass_next_obs_task = [self.create_dev_next_obs_task(pred_dev)]
        else:
            hass_next_obs_task = []

        cum_tasks = hass_dev_tasks + hass_per_tasks + hass_next_obs_task

        """
        return_exceptions means, that exception aren't raised anymore
        but are returned in the result
        """
        results = []
        try:
             # waits for all the tasks to be completed,
            # future is only returned if all tasks returned a future
            results = await asyncio.wait_for(
                asyncio.gather(*cum_tasks, return_exceptions=True),
                timeout=5
            )
        except TimeoutError:
            print('post took to long... resuming')
        self.handle_results_update_hass(results)

    def handle_results_update_hass(self, results):
        """
        is for error handling if one device couldn't be updated
        :param results:
        :return:
        """
        #print(results)
        for result in results:
            if isinstance(result, Exception):
                print(f'Caught exception: {result}')
                #logging.error(f'Caught exception: {result}')

    def create_dev_next_obs_task(self, pred_dev):
        """
        create a task for updateing the most probable next observation
        sensor on homeassistant
        :param pred_dev:
        :return:
        """
        return asyncio.create_task(
            self._create_ws_and_update_dev_next_obs(pred_dev)
        )

    async def _create_ws_and_update_dev_next_obs(self, pred_dev):
        """
        updates a device on homeassistant with a value
        :param pred_name:
        :param value:
        :return:
        """
        new_ws = HassWs(self._url, self._token)
        try:
            await new_ws.connect()
            await new_ws.update_device(
                self._sens_next_obs_name,
                pred_dev
            )
        except asyncio.CancelledError:
            print('cancelled 5')
            # if the task took to long and is cancelled
            await new_ws.disconnect()
            raise
        try:
            await new_ws.disconnect()
        except asyncio.CancelledError:
            print('cancelled 3')
            raise

    def create_person_request_tasks(self, pred_act, pred_act_scores_dict):
        # todo here is an exception thrown IMPORTANT
        tasks = []
        for person in self._per_dict_list:
            # post the new activity to hass
            tasks.append(asyncio.create_task(self._create_ws_and_update_person(
                person['name'], person['id'], pred_act, pred_act_scores_dict
            )))
        return tasks

    async def _create_ws_and_update_person(self, person_name, person_id, pred_act, pred_act_scores_dict):
        """
        updates a device on homeassistant with a value
        :param pred_name:
        :param value:
        :return:
        """
        new_ws = HassWs(self._url, self._token)
        try:
            await new_ws.connect()
            await new_ws.update_person(
                person_name, person_id, pred_act, pred_act_scores_dict)
        except asyncio.CancelledError:
            print('cancelled 5')
            # if the task took to long and is cancelled
            await new_ws.disconnect()
            raise
        try:
            await new_ws.disconnect()
        except asyncio.CancelledError:
            print('cancelled 3')
            raise

    def _create_devices_request_tasks(self, dev_dict):
        tasks = []
        for dev_name in dev_dict:
            #print('--')
            pred_name = ModelManager.dev_name2hb_dev_name(dev_name)
            #print('pred_name: ', pred_name)
            #print('dev_name: ', dev_name)
            score = dev_dict[dev_name]
            #print(score)
            #print('--')
            #print('name: ', pred_name)
            #print('val:  ', value)
            tasks.append(asyncio.create_task(
                self._create_ws_and_update_device(
                    pred_name,
                    score
                )
            ))
        #print('len devs: ', len(dev_dict))
        #print('tasks: ', tasks)
        return tasks


    async def _create_ws_and_update_device(self, pred_name, value):
        """
        updates a device on homeassistant with a value
        :param pred_name:
        :param value:
        :return:
        """
        new_ws = HassWs(self._url, self._token)
        try:
            await new_ws.connect()
            await new_ws.update_device(pred_name, str(value))
        except asyncio.CancelledError:
            print('cancelled 5')
            # if the task took to long and is cancelled
            await new_ws.disconnect()
            raise
        try:
            await new_ws.disconnect()
        except asyncio.CancelledError:
            print('cancelled 3')
            raise

    def gen_state_change_prob_dict(self, xnp1_dict):
        """
        gets a dict with the probabilities for each device and their
        next states (on and off). And compares the devices with the
        actual state in the hass_states dict and returns only the probability
        for each device to be in the different state.

        TLDR: returns probability to change state for each device

        :param xnp1_dict: was generated of a model
            example: { 'binary_sensor.us_distance_mirror' :
                            { 0 : 0.123, 1 : 0.456 } ,... } ,... }
        :return:
            a dictionary mapping of sensors
            example: {'binary_sensor.us_distance_mirror' : 0.123 , ... }

        """
        res_dict = {}
        # as hass_states is a list it is cheaper to loop through
        # the list instead of through the dict
        for entity in self._hass_states:
            if entity['entity_id'] in xnp1_dict:
                if entity['state'] == 'on':
                    res_dict[entity['entity_id']] = 1
                else:
                    res_dict[entity['entity_id']] = 0
        for dev_name in res_dict:
            # get the device state from hass
            #self._hass_states.
            res_dict[dev_name] = xnp1_dict[dev_name][res_dict[dev_name]]
        return res_dict
