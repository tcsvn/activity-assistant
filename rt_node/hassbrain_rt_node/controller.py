import json
import random
import os
import numpy as np
import asyncio
import functools
import signal
from asyncio import CancelledError

from queue import Queue

from hassbrain_rt_node.hass_manager import HomeassistantManager
from hassbrain_rt_node.hassbrain_manager import HassBrainManager
from hassbrain_rt_node.model_manager import ModelManager

"""
todo make two tasks that happen when an event appears
one for prediction the next activity and one for prediciting the next observation
"""
WINDOW_SIZE = 10
INITIAL_VAL = 'init'
SENS_NEXT_OBS = 'next_obs'
RUN_MODE_EVENT = 'event_based'
RUN_MODE_TIMER = 'timer_based'
TIMER_STEPS = 5
# the amount where the probs that are posted to home assistant are rounded
ROUND_FCT = 5

class CustomQueue(object):
    """
        is a qeue of n- elements where the last n relevant observations are
        stored. This is used to predict state and next observation
    """
    def __init__(self, window_size):
        self._obs_window = window_size
        self._obs_seq = Queue()

    def push(self, element):
        """
        pushes element on queue and removes
        the last element if it exceedes the observation window
        :return:
        """
        self._obs_seq.put(element)
        if self._obs_seq.qsize() > self._obs_window:
            self._obs_seq.get()

    def remove_last_pushed(self):
        """
        removes the last element that was pushed onto qeue
        is used if an element caused an error in the model and has
        to be removed
        :return:
        """
        tmp_queue = Queue()
        for j in range(self._obs_seq.qsize()-1):
            tmp_queue.put(self._obs_seq.get())
        self._obs_seq = tmp_queue

    def as_list(self):
        return list(self._obs_seq.queue)

    def as_np_array(self):
        lst = list(self._obs_seq.queue)
        arr = np.array(lst)
        return arr


class Controller(object):

    def __init__(self, hb_address: str, hb_user: str, hb_password: str,
                 model_file: object = None, window_size: int = WINDOW_SIZE) -> None:
        """

        Parameters
        ----------
        hb_address
            the address of the hassbrain instance
                e.g.: http://192.168.10.20:8000
        hb_user
            the name of the user that is allowed to post and get
                e.g.: admin
        hb_password
            the password of the specified user
                e.g: asdf
        model_file
        window_size

        Attributes
        ----------
        self._exit_flag (bool)
            is set to signal an exit for other tasks if for eg an exception arises

        self._run_mode (str)
            is one of the following ( event_based | timer_based )
                event_based
                    listens for events on home assistant and
                timer_based
                    for every timestep the hass state is fetched and an
                    inference step is computed
        """

        self._hb_manager = self._init_hb_manager(hb_address, hb_user, hb_password)
        self._hass_manager = self._init_hass_manager()

        self._raw_obs_queue = CustomQueue(3)
        self._feature_obs_queue = CustomQueue(window_size)

        self._model_manager = self._init_model_manager()

        self._exit_flag = False

        # todo move these stuff where it belongs
        # todo debug remo lines below
        #self._init_run_mode()
        self._run_mode = RUN_MODE_TIMER
        self._time_steps = TIMER_STEPS
        """
        contains a mapping between the names of a device and
        the ids of the new prediction devices on hassbrain api 
        """

        """
        is a qeue of n- elements where the last n relevant observations are 
        stored. This is used to predict state and next observation 
        """
    def _init_run_mode(self):
        self._run_mode = self._model_manager.get_run_mode()
        if self._run_mode == RUN_MODE_TIMER:
            self._time_steps = self._model_manager.get_timesteps()

    def _init_model_manager(self):
        return ModelManager(
            model_file=self._hb_manager.get_model_file(),
            dev_dict=self._hb_manager.get_dev_dict(),
            act_dict=self._hb_manager.get_act_dict(),
        )

    def _init_hb_manager(self, hb_address, hb_user, hb_password):
        hb_man = HassBrainManager(hb_address, hb_user, hb_password, ROUND_FCT)
        hb_man.flush_hassbrain()
        return hb_man

    def _init_hass_manager(self):
        hass_ws = self._hb_manager.create_HassWS_from_api()
        hass_man = HomeassistantManager(hass_ws, INITIAL_VAL,
            self._hb_manager.get_per_dict_list(), SENS_NEXT_OBS,
                                        ROUND_FCT)

        asyncio.run(hass_man.flush_homeassistant(
            dev_dict=self._hb_manager.get_dev_dict(),
            create_dev=True
        ))

        # todo check, return tasks and do error handling
        #asyncio.gather(self._get_hass_states(self._hass_ws),
        #               self._flush_hass(self._hass_ws)
        #               )
        return hass_man

    def _register_signal_handler(self, event_loop):
        for signame in {'SIGINT', 'SIGTERM'}:
            event_loop.add_signal_handler(
                getattr(signal, signame),
                functools.partial(asyncio.ensure_future, self.on_exit(signame))
            )


    def run(self):
        loop = asyncio.new_event_loop()
        self._register_signal_handler(loop)

        if self._run_mode == RUN_MODE_EVENT:
            task = self._handle_exception(self._event_task(), loop)
        elif self._run_mode == RUN_MODE_TIMER:
            task = self._handle_exception(self._timer_task(), loop)
        else:
            raise ValueError
        try:
            loop.create_task(task)
            loop.run_forever()
        finally:
            loop.stop()
            #loop.close()


    async def _handle_exception(self, coro, loop):
        try:
            await coro
        except CancelledError as ex:
            print('lbul'*100)
        except Exception as ex:
            print('lbnlbhll'*100)
            print(ex)
            loop.stop()
            loop.close()

    async def _timer_task(self):
        while True:
            try:
                await asyncio.sleep(self._time_steps)
                await self._process_timed_event()
                if self._exit_flag:
                    break
            except CancelledError as ex:
                break

    async def _event_task(self):
        """
        even though it is in the event loop run this in a while true
        because if there is an error redo everything
        :return:
        """
        while True:
            try:
                await self._hass_manager.connect_websocket()
                await self._hass_manager._hass_ws.listen_states_changed(self._process_event)
                if self._exit_flag:
                    break
            except TypeError as ex:
                await self._hass_manager.disconnect_websocket()
                # this is the case if a device is given to the model,
                # that the model currently doesn't value
                print('lulu')
                print(ex)
                await asyncio.sleep(3)
            except CancelledError as ex:
                break
            except Exception as ex:
                print('*'*100)
                print(ex)
                print('*'*100)

    async def on_exit(self, signame):
        #print("got signal %s: exit" % signame)
        self._exit_flag = True
        await self.on_exit_cleanup_homeassistant()
        self.on_exit_cleanup_hassbrain()
        await self.cancel_all_tasks_in_loop()

    def _print_asyncio_tasks(self):
        print('all_tasks:')
        [print('\t', t) for t in asyncio.all_tasks() if True]
        print('current_task: \n', asyncio.current_task())

    async def cancel_all_tasks_in_loop(self):
        tasks = [t for t in asyncio.all_tasks() if t is not
                 asyncio.current_task()]
        # tod
        [task.cancel() for task in tasks]
        await asyncio.gather(*tasks)
        loop = asyncio.get_event_loop()
        loop.stop()

    async def on_exit_cleanup_homeassistant(self):
        await self._hass_manager.flush_homeassistant(
            dev_dict=self._hb_manager.get_dev_dict(),
            create_dev=False
            )
        await self._hass_manager.disconnect_websocket()

    def on_exit_cleanup_hassbrain(self):
        self._hb_manager.delete_preddevices()
        self._hb_manager.delete_predactivities()
        self._hb_manager.deactivate_persons_rt_pred()


    async def _process_timed_event(self):
        """
        receives an event from homeassistant and handles it
        :param event_dict:
            is a dictionary
        :return:
        """
        print('~'*10)
        obs_seq = self._raw_obs_queue.as_list()
        try:
            hass_dict = await self._hass_manager.get_hass_states()
            raw_obs = self._model_manager.hass_dict2obs_symbol(hass_dict, obs_seq)
            debug1 = self._raw_obs_queue.as_np_array()
            debug2 = self._feature_obs_queue.as_np_array()
            feat_obs, raw_obs = self._model_manager.obs2_featured_obs(
                raw_obs,
                self._raw_obs_queue.as_np_array(),
                self._feature_obs_queue.as_np_array()
            )
            self._raw_obs_queue.push(raw_obs)
            self._feature_obs_queue.push(feat_obs)

            debug3 = self._raw_obs_queue.as_np_array()
            debug4 = self._feature_obs_queue.as_np_array()


        except Exception as ex:
            print('*'*100)
            print(ex)
            print('error in transformation and gathering of hass_states -> obs_symbol')
            print('*'*100)
        obs_seq = self._feature_obs_queue.as_np_array()
        try:
            pred_act, pred_act_scores_dict, predicted_device, temp_xnp1_dict \
                = self._model_manager.create_statistics(obs_seq)
            dev_prob_change = temp_xnp1_dict
            print('pred_act: ', str(pred_act))
            print('pred_act_scd: ', str(pred_act_scores_dict))
            print('pred_dev: ', str(predicted_device))
            print('temp_xnp1_dc: ', str(temp_xnp1_dict))
            # translate
            #if temp_xnp1_dict:
            #    dev_prob_change = self._hass_manager.gen_state_change_prob_dict(temp_xnp1_dict)
            #else:
            #    dev_prob_change = None
        except Exception as e:
            #self._model_manager.reload_model()
            self._raw_obs_queue.remove_last_pushed()
            # don't update anything and return to normal loop
            print('error in model inference')
            print('there may be a mismatch between device names and trained names')
            print('nothing is updated')
            print('exception: ', e)
            return
            #raise

        # update homeassistant and the hassbrain api
        # todo costs ~3 seconds!!! solve with asynchronous library
        self._hb_manager.update_hassbrain(dev_prob_change, pred_act_scores_dict)

        # update the hassbrain device: hassbrain.nextobs with the next pred device
        await self._hass_manager.update_homeassistant(
            pred_act, pred_act_scores_dict, predicted_device,
            dev_prob_change)
        print('finished iteration')



    async def _process_event(self, event_dict):
        """
        receives an event from homeassistant and handles it
        :param event_dict:
            is a dictionary
        :return:
        """
        if not self._model_manager.is_event_relevant(event_dict):
            return

        obs_symbol = self._model_manager.event_dict2obs_symbol(event_dict)
        self._raw_obs_queue.push(obs_symbol)
        obs_seq = self._raw_obs_queue.as_list()
        #print('obs_seq: ', obs_seq)
        try:
            # todo do i have to do this (line below) everytime??
            await self._hass_manager.sync_hass_states()
            pred_act, pred_act_scores_dict, predicted_device, temp_xnp1_dict \
                = self._model_manager.create_statistics(obs_seq)
            # translate
            dev_prob_change = self._hass_manager.gen_state_change_prob_dict(temp_xnp1_dict)
        except Exception as e:
            #self._model_manager.reload_model()
            self._raw_obs_queue.remove_last_pushed()
            # don't update anything and return to normal loop
            print('error in model inference')
            print('there may be a mismatch between device names and trained names')
            print('nothing is updated')
            print('exception: ', e)
            return
            #raise

        # update homeassistant and the hassbrain api
        # todo costs ~3 seconds!!! solve with asynchronous library
        #self._hb_manager.update_hassbrain(dev_prob_change, pred_act_scores_dict)

        # update the hassbrain device: hassbrain.nextobs with the next pred device
        await self._hass_manager.update_homeassistant(
            pred_act, pred_act_scores_dict, predicted_device,
            dev_prob_change)


    def _print_pred_act_score(self, pred_act_scores_dict):
        print('*'*10)
        print('prdactscr: ')
        for pred_act, score in pred_act_scores_dict.items():
            print('pred_act: ' + str(pred_act) + ":\t" + str(score))
        print('--')
        print('practdct: ', self._model_manager._pred_act_dict)
        for pred_act, score in self._model_manager._pred_act_dict['chris'].items():
            print('act_mapping: ' + str(pred_act) + ":\t" + str(score))
        print('perdct: ', self._model_manager._per_dict_list)
        print('*'*10)


    def print_model_info(self):
        print('~'*10)
        print(self._model_manager._model)
        print(self._model_manager._model._obs_lbl_hashmap)
        print(self._model_manager._model._obs_lbl_rev_hashmap)
        print(self._model_manager._model._state_lbl_hashmap)
        print(self._model_manager._model._state_lbl_rev_hashmap)
        print('~'*10)

    #def _update_dummy(self, ):
    #    DEVICE_0_NAME = "switch_printer"
    #    DEVICE_0_STATE_0 = "0.003"
    #    DEVICE_0_STATE_1 = "0.1"
    #    DEVICE_1_NAME = "switch_chris_computer"
    #    DEVICE_1_STATE_0 = "0.003"
    #    DEVICE_1_STATE_1 = "0.1"
    #    tasks = []
    #    tasks.append(asyncio.create_task(self._hass_ws.update_device(
    #                #DEVICE_0_NAME, DEVICE_0_STATE_0)),
    #                DEVICE_0_NAME, DEVICE_0_STATE_1))
    #    )
    #    tasks.append(
    #            asyncio.create_task(self._hass_ws.update_device(
    #                DEVICE_1_NAME, DEVICE_1_STATE_0))
    #                #DEVICE_1_NAME, DEVICE_1_STATE_1))
    #    )
    #    print(tasks)
    #    return tasks





    # todo different main program
    #async def shutdown(signal, loop):
    #    logging.info(f'Received exit signal {signal.name}...')
    #    tasks = [t for t in asyncio.all_tasks() if t is not
    #             asyncio.current_task()]

    #    [task.cancel() for task in tasks]

    #    logging.info('Canceling outstanding tasks')
    #    await asyncio.gather(*tasks)
    #    logging.info('Outstanding tasks canceled')
    #    loop.stop()
    #    logging.info('Shutdown complete.')


    #if __name__ == '__main__':
    #    loop = asyncio.get_event_loop()

    #    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    #    for s in signals:
    #        loop.add_signal_handler(
    #            s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    #    shielded_coro = asyncio.shield(cant_stop_me())

    #    try:
    #        loop.run_until_complete(shielded_coro)
    #    finally:
    #        logging.info('Cleaning up')
    #        loop.stop()
