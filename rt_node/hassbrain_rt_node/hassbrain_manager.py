import hassbrainapi.activity_prediction as hba_act_pred
import hassbrainapi.device_prediction as hba_dev_pred
import hassbrainapi.server as hba_server
import hassbrainapi.device as hba_dev
import hassbrainapi.device_component as hba_comp
import hassbrainapi.person as hba_per
import hassbrainapi.activity as hba_act
import hassbrainapi.rt_node as hba_rt_node
import hassbrainapi.util as hba_util
import hassbrainapi.model as hba_model
import json

from homeassistant_api.websocket import HassWs

from hassbrain_rt_node.model_manager import ModelManager


class HassBrainManager():

    def __init__(self, hb_address, hb_user, hb_password, round_fct):
        """
        :param hb_address:
        :param hb_user:
        :param hb_password:
        :param round_fct:


        :var act_dict:
            is a list ??? todo
            dictionary dump from hassbrain api
            example: [ {'id': 11, 'name':'dental_care', ..., }, ... ]

        :var round_fct
            the amount the probabilities are rounded. is defined in the controller

        :var dev_dict:
            dictionary maps device names to dictionarys todo check what is in dicts
            example: { 'ping_chris_pc.pir_motion_mirror' : { 0 : '1', 2 : 2 }} , ... }
            # todo
            dev_dict = { 'name1' : { 'symb_on' : 'test', 'symb_off' : 'test' }, name2 : { ... } ,...}

        :var dev_id_map
            mapping between device names and the ids of the hassbrain api
            example: { 'binary_sensor.ping_chris_laptop' : 1, ... }

        :var model_file
            Byte object

        :var per_dict_list
            dump of hassbrain apis person json objects
            example: [{'id': 15, 'name': 'chris', ... }, ... ]

        :var pred_act_dict
            mapping of persons and their names of activities with the id of the corresponding hassbrain api object
            example: {'chris' : {'id': 15, 'dental_care' : 1385, 'enter_home':1338, ... } , ... }

        :var pred_dev_dict
            mapping of device names to their corresponding id of predicted_device object on the hassbrain api

        """
        self._hb_address = hb_address
        self._hb_user = hb_user
        self._hb_pw = hb_password
        self._round_fct = round_fct
        self._act_dict = {}

        """

        """
        self._dev_dict = {}
        self._model_file = None
        self._per_dict_list = []
        self._pred_dev_dict = {}
        self._pred_act_dict = {}
        self._dev_id_map = {}


        self._act_dict = hba_act.get(self._hb_address, self._hb_user, self._hb_pw)

        # craete get dev dict
        hba_dev_dict = hba_dev.get(self._hb_address, self._hb_user, self._hb_pw)
        hba_comp_dict = hba_comp.get(self._hb_address, self._hb_user, self._hb_pw)
        self._dev_dict, self._dev_id_map = self._create_devices(hba_dev_dict, hba_comp_dict)

        rt_node_dict = hba_rt_node.get(self._hb_address, self._hb_user, self._hb_pw)[0]
        self._rt_node_id = int(rt_node_dict['id'])

        # todo later add support for multiple persons per model
        model_url = rt_node_dict['model']
        model_dict = hba_model.get_by_address(model_url, self._hb_user, self._hb_pw)
        model_file_url = model_dict['file']
        self._model_file = hba_model.download_model(model_file_url)

        # get the person information, ...
        assert model_dict['person'] is not None
        self._per_dict_list = self._person_url_list2per_dict_list(
            [model_dict['person']])

        self._multiple_person = len(self._per_dict_list) > 1
        # link rt node to server
        # todo maybe better place in controller
        self._link_rt_node2server(self._rt_node_id)


    def get_model_file(self):
        return self._model_file

    def get_dev_dict(self):
        return self._dev_dict

    def get_act_dict(self):
        return self._act_dict

    def get_per_dict_list(self):
        return self._per_dict_list

    def flush_hassbrain(self):
        """
        cleanup the hassbrain api from previous runs and create the devices needed for all stuff
        :return:
        """
        self.delete_preddevices()
        self._pred_dev_dict = self.create_preddevices(self._dev_dict, self._dev_id_map)

        """
        contains the person, its id's and the predicted activity names and corre
         sponding ids for updating the values
        dev_dict = { person_name : { 'id' : 'per_id=0', 'activity3_name' : 17, ... }, ... }
        """
        self.delete_predactivities()
        self._pred_act_dict = self.create_predactivities()

        """
        """
        self.activate_persons_rt_pred()


    def create_HassWS_from_api(self):
        server_dict = hba_server.get(self._hb_address, self._hb_user, self._hb_pw)
        hass_address = server_dict['hass_address']
        api_token = server_dict['hass_api_token']
        return HassWs(hass_address, api_token)

    def _person_url_list2per_dict_list(self, person_url_list):
        """
        a list of urls of persons that are predicted by the model
        :param person_url_list:
        :return:
        """
        per_dict_list = []
        for person_url in person_url_list:
            per_dict_list.append(hba_per.get_by_address(
                person_url, self._hb_user, self._hb_pw)
            )
        return per_dict_list


    def _create_devices(self, hb_dev_dict, hb_comp_dict):
        """
        creates dictionary for devices
        :param hb_dev_dict:
        :param hb_comp_dict:
        :return:
        """
        hb_dev_name_id_hashmap = {}
        # 1. concatenate
        res_dict = {}
        for device in hb_dev_dict:
            if device['location'] is not None:
                name = device['name']
                comp = self._comp_url_2_comp(device['component'], hb_comp_dict)
                entity_id = comp + "." + name
                res_dict[entity_id] = {}
                hb_dev_name_id_hashmap[entity_id] = device['id']
        return res_dict, hb_dev_name_id_hashmap

    def _comp_url_2_comp(self, comp_url, hb_comp_dict):
        comp_id = int(comp_url[-2:-1])
        for item in hb_comp_dict:
            if int(item['id']) == comp_id:
                return item['name']

    def _link_rt_node2server(self, ide):
        rt_node_url = hba_util.rt_node_id2rt_node_url(self._hb_address, ide)
        resp = hba_server.put(self._hb_address, self._hb_user, self._hb_pw,
                              rt_node_url=rt_node_url + "/")

    def activate_persons_rt_pred(self):
        self.set_persons_rt_pred(True)

    def deactivate_persons_rt_pred(self):
        self.set_persons_rt_pred(False)

    def set_persons_rt_pred(self, value):
        for person in self._per_dict_list:
            print(person)
            hba_per.put(
                self._hb_address,
                self._hb_user,
                self._hb_pw,
                id=person['id'],
                prediction=value
            )

    def update_hassbrain(self, xnp1_dict, pred_act_scores_dict):
        # update hassbrain web instance with actualized stuff
        self.update_hassbrain_persons(pred_act_scores_dict)
        self.update_hassbrain_devices(xnp1_dict)

    def update_hassbrain_persons(self, pred_act_scores_dict):
        """
        posts the changes of the predicted activites for each person
        to the hassbrain api
        :param pred_act_scores_dict:
        :return: None
        """
        for person in self._per_dict_list:
            per_name = person['name']
            for activity in pred_act_scores_dict:
                act_pred_id = self._pred_act_dict[per_name][activity]
                score = pred_act_scores_dict[activity]
                hba_act_pred.put(self._hb_address, self._hb_user, self._hb_pw,
                    act_pred_id, score)

    def delete_predactivities(self):
        """
        """
        pred_acts = hba_act_pred.get(self._hb_address, self._hb_user, self._hb_pw)
        for dev in pred_acts:
            hba_act_pred.delete_by_id(self._hb_address, self._hb_user, self._hb_pw,
                dev['id'])

    def create_predactivities(self):
        """

        :param act_dict:
        :param pred_dev_hm:
             Dictionary of device names and their corresponding hassbrain id
             { 'binary_sensor.motion_bed' : 5, ... }
        :return:
        """
        # create hashmap of ids for later updating
        #print('='*100)
        #print(self._per_dict_list)
        #print(self._act_dict)
        pred_act_dict = {}
        for person in self._per_dict_list:
            for activity in self._act_dict:
                score = 0.0
                resp = hba_act_pred.create_with_ids(
                    self._hb_address,
                    self._hb_user,
                    self._hb_pw,
                    person_id=person['id'],
                    activity_id=activity['id'],
                    score=score)
                #print('lululu'*10)
                #print(resp.content)
                #print('lululu'*10)
                ide = json.loads(resp.content)['id']
                try:
                    pred_act_dict[person['name']][activity['name']] = ide
                except:
                    pred_act_dict[person['name']] = {}
                    pred_act_dict[person['name']]['id'] = person['id']
                    pred_act_dict[person['name']][activity['name']] = ide
        return pred_act_dict

    def update_predactivities(self, person, activity, score):
        ide = self._pred_act_dict[person][activity]
        hba_act_pred.put(
            self._hb_address,
            self._hb_user,
            self._hb_pw,
            ide=ide,
            score=score)

    def delete_preddevices(self):
        """
        deletes all prediction devices at the hassbrain rest api
        :return:
        """
        #print('='*100)
        device_dict = hba_dev_pred.get(
            self._hb_address,
            self._hb_user,
            self._hb_pw)
        #print(device_dict)

        for dev in device_dict:
            hba_dev_pred.delete(
                self._hb_address,
                self._hb_user,
                self._hb_pw,
                dev['id'])

    def create_preddevices(self, dev_dict, pred_dev_hm):
        """

        :param dev_dict:
        :param pred_dev_hm:
             Dictionary of device names and their corresponding hassbrain id
             { 'binary_sensor.motion_bed' : 5, ... }
        :return:
        """
        # create hashmap of ids for later updating
        pred_dev_dict = {}
        for dev in dev_dict:
            ide = pred_dev_hm[dev]
            dev_url = hba_util.create_device_url(self._hb_address, ide)
            rt_node_url = hba_util.rt_node_id2rt_node_url(
                self._hb_address, self._rt_node_id)
            score = 0.0
            #print('rt_node_url: ', rt_node_url)
            #print('dev_url: ', dev_url)
            resp = hba_dev_pred.create(
                self._hb_address,
                self._hb_user,
                self._hb_pw,
                # todo doesn't work without trailing '/'
                # todo therefore check url creation
                rt_node_url=rt_node_url + "/",
                device_url=dev_url + "/",
                score=score)
            ide = json.loads(resp.content)['id']
            pred_dev_dict[dev] = ide
        return pred_dev_dict



    def update_hassbrain_devices(self, dev_dict):
        for dev_name in dev_dict:
            # todo line below flag for deletion
            #pred_name = ModelManager.dev_name2hb_dev_name(dev_name)
            score = dev_dict[dev_name]
            self._update_preddevice(dev_name, round(score, self._round_fct))

    def _update_preddevice(self, name, score):
        ide = self._pred_dev_dict[name]
        hba_dev_pred.put(
            self._hb_address,
            self._hb_user,
            self._hb_pw,
            ide=ide,
            score=score)

