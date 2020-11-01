import joblib
import numpy as np
from hassbrain_algorithm.datasets._dataset import DataRep

class ModelManager():

    def __init__(self, dev_dict, act_dict, model_file):
        """

        Parameters
        ----------
        dev_dict
        act_dict
        model_file

        Attributes
        ---------

        """
        self._dev_dict = dev_dict
        self._act_dict = act_dict
        self._model_file = model_file
        self._model = joblib.load(model_file) # type: Model
        # todo get observation type from model
        #self._model.get_observation_dist()
        self._observation_repr = 'bernoulli'
        #self._dev_list = self._model.get_dev_list()


    def create_statistics(self, obs_seq):
        pred_act = self._model.classify(obs_seq)
        pred_act_scores_dict = self._model.classify_multi(obs_seq)

        predicted_device = {}
        xnp1_dict = {}
        if self._model.can_predict_prob_devices():
            xnp1_dict = self._model.predict_prob_xnp1(obs_seq)
        if self._model.can_predict_next_obs():
            predicted_device = self._model.predict_next_obs(obs_seq)

        return pred_act, pred_act_scores_dict, predicted_device, xnp1_dict

    def reload_model(self):
        self._model = joblib.load(self._model_file) # type: Model


    def activity_name2id(self, act_name):
        """

        :param act_name:
        :return:
        """
        for activity in self._act_dict:
            if activity['name'] == act_name:
                return activity['id']
        raise KeyError

    def hass_dict2obs_symbol(self, hass_entitys, obs_seq):
        """

        Parameters
        ----------
        hass_entitys (lst)
            [ { 'entity_id': 'binary_sensor.ping_chris_pc',
                'state': 'off',
                'attributes': {'friendly_name': 'ping_chris_pc'},
                'last_changed': '2019-07-06T11:59:17.905179+00:00',
                'last_updated': '2019-07-06T11:59:17.905179+00:00',
                'context': {'id': '9d41808d02dc4d5a8bb3e28cd611fd1a',
                            'parent_id': None,
                             'user_id': None}
                }, ... { ... } ]
        obs_seq (lst)
            the last observations
        Returns
        -------
            np. array 1d
                [1,0,1,0,0,1,0,0]

        """
        hass_ent2 = self._hass_dict2obs_symbol_filter_list(hass_entitys)
        return self._hass_dict2obs_symbol_create_vector(hass_ent2)

    def obs2_featured_obs(self, obs, raw_obs_seq, feat_obs_seq):
        """ changes the raw observation into the representation the model was
        trained on. also
        Parameters
        ----------
        obs (lst)
            is the observation
        raw_obs_seq (np.array)
            contains the last two raw observations
        feat_obs_seq (np.array)
            contains the last N featured observations
        Returns
        -------
            featured obs array 1d
                [0,0,1,0,0,1,0,0]
            x obs array 1d
                [1,0,1,0,0,1,0,1]
        """
        if self._model.get_data_repr() == DataRep.RAW:
            return obs, obs

        elif self._model.get_data_repr() == DataRep.LAST_FIRED:
            return self._raw_bernoulli2lastfired(obs, raw_obs_seq, feat_obs_seq)

        elif self._model.get_data_repr() == DataRep.CHANGEPOINT:
            return self._raw_bernoulli2changepoint(obs, raw_obs_seq)

    def _raw_bernoulli2lastfired(self, x: np.ndarray, raw_obs_seq: np.ndarray, feat_obs_seq: np.ndarray) -> [np.ndarray, np.array]:
        """

        Parameters
        ----------
        x (np.array)
            vector array[0,0,0,1,1,0,0,0,1]

        obs_seq (list)
            list of vectors
                [ array[...], array[...], ... ]
        Returns
        -------
        feature vector(np.array)
            vector array[0,0,0,1,1,0,0,0,1]
        raw vector(np.array)
            vector array[0,0,0,1,1,0,0,0,1]

        """

        raw = x.copy()
        # at the times of multiple changes
        if raw_obs_seq.size == 0:
            # set all to false
            idx = np.where(x == True)[0]
            res = self._create_all_false_with_idx_true(idx[0], x.shape)
            return res, raw

        previous_obs = raw_obs_seq[-1:][0]
        diff = np.logical_xor(previous_obs, x) #type: np.ndarray
        if np.any(diff):
            # check if there is at least one difference
            idxs = np.where(diff == True)[0]
            if len(idxs) == 1:
                res = self._create_all_false_with_idx_true(idxs[0], x.shape)
                return res, raw
            else:
                # choose random idx
                idx = idxs[np.random.randint(0,len(idxs))]
                res = self._create_all_false_with_idx_true(idx, x.shape)
                idxs = idxs.tolist()
                idxs.remove(idx)
                """
                change raw at the following steps in order to pass the change
                to the next generation
                """
                for i in idxs:
                    raw[i] = not raw[i]
                return res, raw
        else:
            # this is the case when they are not different
            tmp = feat_obs_seq[-1:][0]
            return tmp, raw

    def _create_all_false_with_idx_true(self, idx, shape):
        """
        Parameters
        ----------
        idx (int)
            the index
        shape (np.shape)
            the shape of the vector to create
        Returns
        -------
        """
        all_false = np.zeros(shape=shape, dtype=bool)
        all_false[idx] = True
        return all_false

    def _raw_bernoulli2changepoint(self, x: np.ndarray, raw_obs_seq: np.ndarray) -> [np.ndarray, np.array]:
        """

        Parameters
        ----------
        x (np.array)
            vector array[0,0,0,1,1,0,0,0,1]

        obs_seq (list)
            list of vectors
                [ array[...], array[...], ... ]
        Returns
        -------
        feature vector(np.array)
            vector array[0,0,0,1,1,0,0,0,1]
        raw vector(np.array)
            vector array[0,0,0,1,1,0,0,0,1]

        """

        raw = x.copy()
        res = np.zeros_like(x, dtype=bool)
        # at the times of multiple changes
        if raw_obs_seq.size == 0:
            # set all feature to false as it is not known if sth has changed from befor
            return res, raw

        previous_obs = raw_obs_seq[-1:][0]
        diff = np.logical_xor(previous_obs, x) #type: np.ndarray
        if np.any(diff):
            # check if there is at least one difference
            # then create vector with fields true where index has changed
            idxs = np.where(diff == True)[0]
            for i in idxs:
                res[i] = True
            return res, raw
        else:
            # this is the case when they are not different
            return res, raw

    def _hass_dict2obs_symbol_create_vector(self, hass_entitiys):
        """
        create from a hass entity list the observation vector with on and
        off encoded as one and zero
        Parameters
        ----------
        hass_entitiys
            [ { 'entity_id': 'binary_sensor.ping_chris_pc',
                'state': 'off'
            } .. ]
        Returns
        -------
            numpy nd array 1D vector with the length of the observations from
            the model
            e.g.:
                [1,0,0,1,1,0]
        """
        obs_lbl_list = self._model.get_obs_lbl_lst()
        x = np.zeros((len(obs_lbl_list)), dtype=np.int64)
        for entity in hass_entitiys:
            lbl = entity['entity_id']
            idx = self._model.encode_obs_lbl(lbl)
            if entity['state'] == 'on':
                x[idx] = 1
            elif entity['state'] == 'off':
                x[idx] = 0
            else:
                print('spiderman')
                raise ValueError
        return x

    def _hass_dict2obs_symbol_filter_list(self, hass_entitys):
        """

        Parameters
        ----------
        hass_entitys

        Returns
        -------
            new_lst <class 'list'>
            [{ 'entity_id': 'binary_sensor.ping_chris_smartphone',
             'state': 'off'},
             {'entity_id': 'binary_sensor.us_distance_monitor_left',
              'state': 'off'}, ... ]
        """
        new_lst = []
        for entity in hass_entitys:
            dev_name = entity['entity_id']
            if self._is_source_in_dev(dev_name):
                new_entity = {}
                new_entity['entity_id'] = dev_name
                new_entity['state'] = entity['state']
                new_lst.append(new_entity)
        return new_lst

    def event_dict2obs_symbol(self, event_dict):
        """
        :param event_dict:
        :return:
            a tuple containing the name of the device and its state
            encoded in 1 or 0
        """
        data = event_dict['event']['data']
        dev_name = data['entity_id']
        new_state = data['new_state']['state']
        if new_state == "on":
            new_state = 1
        else:
            new_state = 0
        return (dev_name, new_state)

    def _is_event_a_state_change(self, event_dict):
        return not event_dict['type'] == 'result' \
            and event_dict['event']['event_type'] == 'state_changed'

    def is_event_relevant(self, event_dict):
        # exclude all irrelevant events what remains must be true
        if not self._is_event_a_state_change(event_dict):
            return False

        # if event appears than execute function of hb
        data = event_dict['event']['data']
        dev_name = data['entity_id']
        if not self._is_source_in_dev(dev_name):
            return False
        return True

    @classmethod
    # todo maybe move to hass_manager
    def dev_name2hb_dev_name(cls, name: str):
        """
            this is the representation that homeassistant devices use
            example:
                'binary_sensor.test3' -> binary_sensor_test3
                in homeassistant under hassbrain.binary_sensor_test3
        :param name:
        :return:
        """
        return name.replace('.', '_')

    def _is_source_in_dev(self, device_name):
        """
        checks if the device that caused the event in homeassistant
        is inside the devices list that are observed by the model
        :return:
            Boolean True or False
        """
        device_in_list = False
        for dev_name in self._dev_dict:
            if dev_name == device_name:
                device_in_list = True
                break
        return device_in_list
