from backend.models import *
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.shortcuts import render
import requests
import json

import os
from frontend.forms import ModelForm
from homeassistant_api.websocket import HassWs
import homeassistant_api.rest as hass_api

from backend.models import Algorithm, Benchmark


DATASET_NAME_HASS="homeassistant"
HASS_DB_NAME = 'home-assistant_v2.db'
MODEL_FILE_NAME = "model.joblib"
MODEL_IMG_NAME = "visualization.png"
TRAIN_LOSS_FILE_NAME = "trainloss.csv"
TRAIN_LOSS_IMG_NAME = "trainloss.png"
TRAIN_ACC_FILE_NAME = "trainacc.csv"
TRAIN_ACC_IMG_NAME = "trainacc.png"


class AlgorithmTrainingView(TemplateView):
    pass

class AlgorithmView(TemplateView):
    # list all persons and render them into the frontend

    def is_algorithm_selected(self):
        server = Server.objects.all()[0]
        return server.selected_algorithm is not None

    def is_algorithm_trained(self, algorithm_selected=None):
        """
        checks if a model exists, that is trained on the dataset, algorithm
        and person combination
        :param algorithm_selected:
        :return:
        """
        if algorithm_selected is None:
            return self.exists_model_for_selection()
        if not algorithm_selected:
            return False
        else:
            return self.exists_model_for_selection()

    def exists_model_for_selection(self):
        algorithm = self.get_sel_algorithm()
        return self.exists_model_comb(
                algorithm,
                algorithm.selected_person,
                algorithm.selected_dataset
        )

    def exists_model_comb(self, algorithm, person, dataset):
        """
        checks if a model with these combination exists
        :param algorithm:
        :param dataset:
        :param person:
        :return:
        """
        try:
            model = Model.objects.filter(algorithm=algorithm,
                     person=person,
                     dataset=dataset)[0]
            model_exists = model is not None
        except:
            model_exists = False
        return model_exists

    def get_sel_model(self):
        algo = self.get_sel_algorithm()
        return Model.objects.filter(algorithm=algo,
                                    person=algo.selected_person,
                                    dataset=algo.selected_dataset)[0]

    def is_model_evaluated(self, model):
        return hasattr(model, 'benchmark')

    def is_realtime_node_running(self):
        srv = Server.objects.all()[0]
        return srv.realtime_node is not None

    def is_hass_comp_model_selected(self):
        """
        checks if the selected algorithm was trained on the
        homeassistant dataset.
        Is used to show or not show the button run
        :return:
        """
        model = self.get_sel_model()
        if hasattr(model, 'dataset'):
            return model.dataset.name == DATASET_NAME_HASS
        else:
            return False

    def generate_data_for_model_comparision(self):
        #person_name = "chris"
        #dataset_name = "hass_testing"

        #dataset = Dataset.objects.filter(name=dataset_name)[0]
        #person = Person.objects.filter(name=person_name)[0]

        # get models that satisfy this constraint
        # todo implement

        # create list from models
        # todo implement

        #example file
        bench_model_list = \
            [
                {'name' : 'HMM',
                 'acc' : 0.9,
                 'prec' : 0.8,
                 'rec' : 0.7,
                 'f1': 0.6},
                {'name' : 'ESHMM',
                 'acc' : 0.9,
                 'prec' : 0.8,
                 'rec' : 0.7,
                 'f1': 0.6},
                {'name' : 'PCHMM',
                 'acc' : 0.1,
                 'prec' : 0.2,
                 'rec' : 0.3,
                 'f1': 0.4},
            ]
        return bench_model_list

    def create_context(self, request):
        algorithm_list = Algorithm.objects.all()
        person_list = Person.objects.all()
        dataset_list = Dataset.objects.all()
        context = {}
        form = ModelForm()
        model_list = Model.objects.all()
        a_sel = self.is_algorithm_selected()
        if a_sel:
            algo = self.get_sel_algorithm()
            a_trn = self.exists_model_comb(
                algo,
                algo.selected_person,
                algo.selected_dataset
            )
            if a_trn:
                model = self.get_sel_model()
                a_eval = self.is_model_evaluated(model)
            else:
                a_eval = False
        else:
            a_trn = False
            a_eval = False

        rt_running = self.is_realtime_node_running()
        context['bench_model_list'] = self.generate_data_for_model_comparision()
        if a_sel:
            context['selected_algorithm'] = self.get_sel_algorithm()
        if a_trn:
            context['model_download_url'] = 'asdf'
            context['model'] = self.get_sel_model()
        if a_trn:
            context['model_is_hass_compatible'] = self.is_hass_comp_model_selected()
        context['person_list'] = person_list
        context['algorithm_list'] = algorithm_list
        context['model_list'] = model_list
        context['dataset_list'] = dataset_list
        context['algorithm_selected'] = a_sel
        context['algorithm_trained'] = a_trn
        context['algorithm_evaluated'] = a_eval
        context['rt_node_running'] = rt_running
        context['form'] = form
        if rt_running:
            pass
            context['predicted_devices'] = Server.objects.all()[0].realtime_node.predicted_devices.all()

        # create
        #        if a_eval:
        #            scores_list = []
        #            algorith.bench

        return context

    def get_sel_algorithm(self):
        return Server.objects.all()[0].selected_algorithm

    def select_algorithm(self, request):
        algo_name = request.POST.get("algorithm", "")
        #person_name = request.POST.get("person_select", "")
        # set algorithm as selected algorithm
        algo = Algorithm.objects.filter(name=algo_name)[0]
        # todo include a person in the html file
        # todo IMPORTANT
        #person = Person.objects.filter(name=person_name)[0]
        server = Server.objects.all()[0]
        server.selected_algorithm = algo
        server.save()
        #algo.selected_person = person
        algo.save()


    def _create_hass_db_path(self):
        hass_address = Server.objects.all()[0].hass_address
        token = Server.objects.all()[0].hass_api_token
        path_to_hass_config = hass_api.get_config_folder(
            hass_address, token
        )
        return path_to_hass_config + "/" + HASS_DB_NAME

    def _create_activity_file_path(self, selected_person):
        """
        given a person create the filepath to its activities

        look in backend_views (194) for reference how the folder and file
        are created and logged to
        :param selected_person:
        :return:
        """
        return settings.HASSBRAIN_ACT_FILE_FOLDER + "/" \
               + selected_person.name + "/" \
               + settings.ACTIVITY_FILE_NAME

    def _create_class_from_name(self, ctrl, algorithm):
        module_name_list = algorithm.class_name.split(".")
        import importlib
        class_name = module_name_list[-1]
        module_path = ".".join(module_name_list[:-1])
        module_name = "hassbrain_algorithm.models." + module_path

        # The file gets executed upon import, as expected.
        module = importlib.import_module(module_name)
        # Then you can use the module like normal

        try:
            hmm_model = getattr(module, class_name)(ctrl)
        except:
            raise ValueError
        return hmm_model

    @classmethod
    def get_location_data(cls):
        """
        generates the location data from the hassbrainapi configuration
        :return:
            list of location dictionarys [ {
                "name" : "loc1",
                "activities" : ['cooking'],
                "devices" : ['binary_sensor.motion_hallway', 'binary_sensor.motion_mirror'],
            },
                {"name" : "loc2",
                 "activities" : ['cooking', 'eating'],
                 "devices" : [],
                 },
                {"name" : "loc3",
                 "activities" : ['sleeping'],
                 "devices" : ['binary_sensor.motion_bed'],
                 },
            ]
        """
        locations = Location.objects.all()
        loc_list = []
        for loc in locations:
            loc_dict = {}
            loc_dict["name"] = loc.name
            loc_dict["activities"] = []
            for activity in loc.activities.all():
                loc_dict["activities"].append(activity.name)
            loc_dict["devices"] = []
            for device in Device.objects.all():
                if device.location == loc:
                    loc_dict["devices"].append(device.component.name + "." + device.name)
            loc_list.append(loc_dict)
        return loc_list

    @classmethod
    def get_activity_data(cls, person):
        """
        generates the activity data of a person from its hassbrainapi configuration
        :param person:
        :return:
        list of activity dictionarys
        example:
        act_data = [
            {"name" : "sleeping",
            "day_of_week" : 0,
            "start" : datetime.time.fromisoformat("04:00:00"),
            "end" : datetime.time.fromisoformat("06:15:00")
            },
            {"name" : "cooking",
            "day_of_week" : 0,
            "start" : datetime.time.fromisoformat("06:15:00"),
            "end" : datetime.time.fromisoformat("08:45:00")
            },
            ... ]
        """
        synth_activities = person.synthetic_activities.all()
        act_data = []
        for syn_act in synth_activities:
            act_data.append({
                'name': syn_act.synthetic_activity.name,
                'day_of_week': syn_act.day_of_week,
                'start': syn_act.start,
                'end': syn_act.end
            })
        #print(act_data)
        return act_data



    def select_dataset(self, request):
        dataset_name = request.POST.get("dataset_select", "")
        dataset = Dataset.objects.filter(name=dataset_name)[0]
        server = Server.objects.all()[0]
        server.selected_dataset = dataset
        server.save()

    def select_model(self, request):
        model_pk = request.POST.get("model_select", "")
        model = Model.objects.get(pk=model_pk)
        algo = self.get_sel_algorithm()
        algo.selected_dataset = model.dataset
        algo.selected_person = model.person
        algo.save()

    def _media_delete_file(self, filename):
        filepath = settings.MEDIA_ROOT + filename
        import os
        ## If file exists, delete it ##
        if os.path.isfile(filepath):
            os.remove(filepath)

    def _train_algorithm_on_preset_dataset_forehand_cleanup(self, algo):
        folder_name = self._generate_folder_name(algorithm=algo, preset_dataset=True)
        # if such a model already exists delete the model
        # and create a new one
        if self.exists_model_comb(algorithm=algo,
                                  person=None,
                                  dataset=algo.selected_dataset):
            model = self.get_sel_model()
            model.delete()
            # delete files
            self._media_delete_file(folder_name + "/" + MODEL_FILE_NAME)
            self._media_delete_file(folder_name + "/" + MODEL_IMG_NAME)
            self._media_delete_file(folder_name + "/" + TRAIN_ACC_FILE_NAME)
            self._media_delete_file(folder_name + "/" + TRAIN_LOSS_FILE_NAME)
            self._media_delete_file(folder_name + "/" + TRAIN_ACC_IMG_NAME)
            self._media_delete_file(folder_name + "/" + TRAIN_LOSS_IMG_NAME)
            self._media_delete_file(folder_name + "/" + TRAIN_LOSS_FILE_NAME)

        print('foldername: ', folder_name)
        self._create_media_model_folder_if_not_exists(folder_name)

    def get_media_file_path(self, folder_name, file_name):
        return settings.MEDIA_ROOT + folder_name + "/" + file_name

    def _clean_tmp_folder(self):
        self._media_delete_file('tmp/' + MODEL_FILE_NAME)
        self._media_delete_file('tmp/' + TRAIN_ACC_FILE_NAME)
        self._media_delete_file('tmp/' + TRAIN_LOSS_FILE_NAME)

    def train_algorithm_on_preset_dataset(self, request):
        dataset_name = request.POST.get("dataset_select", "")
        algo = self.get_sel_algorithm()
        dataset = Dataset.objects.filter(name=dataset_name)[0]
        algo.selected_dataset = dataset
        algo.save()

        self._train_algorithm_on_preset_dataset_forehand_cleanup(algo=algo)
        folder_name = self._generate_folder_name(algorithm=algo, preset_dataset=True)
        tmp_folder_name = 'tmp/' + folder_name

        tmp_model_file_path = self.get_media_file_path(tmp_folder_name, MODEL_FILE_NAME)
        self._create_media_model_folder_if_not_exists(tmp_folder_name)
        tmp_model_image_file_path = self.get_media_file_path(tmp_folder_name, MODEL_IMG_NAME)
        tmp_loss_file_path = self.get_media_file_path(tmp_folder_name, TRAIN_LOSS_FILE_NAME)
        tmp_loss_image_file_path = self.get_media_file_path(tmp_folder_name, TRAIN_LOSS_IMG_NAME)
        tmp_acc_file_path = self.get_media_file_path(tmp_folder_name, TRAIN_ACC_FILE_NAME)


        ctrl = self._create_ctrl_for_normal_dataset(algo, dataset)
        ctrl.init_model_on_dataset()
        ctrl.register_benchmark()

        #ctrl.register_loss_file_path('/home/cmeier/code/tmp/kasteren/train_loss.log')
        ctrl.register_loss_file_path(tmp_loss_file_path)

        print('~'*100)
        print('~'*100)
        print('loss_fn: ', tmp_loss_file_path)
        # todo set file path to acc logs in ctrl
        # todo set file path to train logs in ctrl
        #ctrl.register_acc_file_path(tmp_loss_file_path)
        #ctrl.register_acc_file_path(tmp_acc_file_path)
        #print('acc_fn: ', tmp_acc_file_path)
        #print('~'*100)
        #print('~'*100)

        ctrl.train_model([False])
        # workaround, saving the file beforehand and loading it again
        # because joblib doesn't support buffer stuff
        #self._clean_tmp_folder()

        ctrl.save_model(tmp_model_file_path)
        ctrl.save_loss_plot_to_file(tmp_loss_image_file_path)
        ctrl.save_visualization_to_file(tmp_model_image_file_path)


        from django.core.files.base import File
        from django.core.files.images import ImageFile

        # normal
        django_model_file = File(open(tmp_model_file_path, "rb"))
        django_model_file.name = folder_name + "/" + MODEL_FILE_NAME

        django_model_img = ImageFile(open(tmp_model_image_file_path, "rb"))
        django_model_img.name = folder_name + "/" + MODEL_IMG_NAME

        #django_acc_file = File(open(tmp_acc_file_path, "rb"))
        #django_acc_file.name = folder_name + TRAIN_ACC_FILE_NAME

        django_loss_file = File(open(tmp_loss_file_path, "rb"))
        django_loss_file.name = folder_name + "/" + TRAIN_LOSS_FILE_NAME

        django_loss_image = ImageFile(open(tmp_loss_image_file_path, "rb"))
        django_loss_image.name = folder_name + "/" + TRAIN_LOSS_IMG_NAME

        print(django_model_file.name)

        model = Model(
            algorithm=algo,
            person=algo.selected_person, # can be null
            dataset=algo.selected_dataset,
            file=django_model_file,
            visualization=django_model_img,
            train_loss=django_loss_file,
            train_loss_graph=django_loss_image
            #train_acc=django_acc_file,
            )
        model.save()

        os.remove(tmp_model_file_path)
        os.remove(tmp_loss_file_path)
        #os.remove(tmp_acc_file_path)

    def _create_model_name(self, algo, person, datainstance):
        tmp  = datainstance.name.replace(' ', '_')
        model_name = algo.name + '.' + person.name + '.' + tmp
        return model_name

    def train_algorithm_on_hass_instance(self, request):
        # get web model of dataset
        person_name = request.POST.get("person_select", "")

        algo = self.get_sel_algorithm()
        # todo change this by adding an option in front end to choose data instance
        datainstance = DataInstance.objects.filter(id=2)[0]
        dataset = Dataset.objects.filter(name="homeassistant")[0]
        person = Person.objects.filter(name=person_name)[0]

        algo.selected_person = person
        algo.selected_dataset = dataset
        algo.save()

        model_name = self._create_model_name(algo, person, datainstance)
        folder_name = self._generate_folder_name(algorithm=algo, preset_dataset=False)
        tmp_folder_name = 'tmp/' + folder_name

        tmp_model_file_path = self.get_media_file_path(tmp_folder_name, MODEL_FILE_NAME)
        self._create_media_model_folder_if_not_exists(tmp_folder_name)
        tmp_model_image_file_path = self.get_media_file_path(tmp_folder_name, MODEL_IMG_NAME)
        tmp_loss_file_path = self.get_media_file_path(tmp_folder_name, TRAIN_LOSS_FILE_NAME)
        tmp_loss_image_file_path = self.get_media_file_path(tmp_folder_name, TRAIN_LOSS_IMG_NAME)
        tmp_acc_file_path = self.get_media_file_path(tmp_folder_name, TRAIN_ACC_FILE_NAME)

        ctrl = self._create_ctrl_for_hass_instance(algo, person, datainstance, model_name)
        ctrl.init_model_on_dataset(model_name)
        ctrl.register_benchmark(model_name)
        ctrl.register_loss_file_path(tmp_loss_file_path, model_name)

        ctrl.train_model(model_name)
        # workaround, saving the file beforehand and loading it again
        # because joblib doesn't support buffer stuff
        #self._clean_tmp_folder()

        ctrl.save_model(tmp_model_file_path, model_name)
        ctrl.save_plot_trainloss(model_name, tmp_loss_image_file_path)
        # todo make this work
        #ctrl.save_visualization_to_file(tmp_model_image_file_path, model_name)

        from django.core.files.base import File
        from django.core.files.images import ImageFile

        # normal
        django_model_file = File(open(tmp_model_file_path, "rb"))
        django_model_file.name = folder_name + "/" + MODEL_FILE_NAME

        #django_model_img = ImageFile(open(tmp_model_image_file_path, "rb"))
        #django_model_img.name = folder_name + "/" + MODEL_IMG_NAME

        django_loss_file = File(open(tmp_loss_file_path, "rb"))
        django_loss_file.name = folder_name + "/" + TRAIN_LOSS_FILE_NAME

        django_loss_image = ImageFile(open(tmp_loss_image_file_path, "rb"))
        django_loss_image.name = folder_name + "/" + TRAIN_LOSS_IMG_NAME

        print(django_model_file.name)

        model = Model(
            algorithm=algo,
            person=algo.selected_person, # can be null
            dataset=algo.selected_dataset,
            datainstance=datainstance,
            file=django_model_file,
            #visualization=django_model_img,
            visualization=None,
            train_loss=django_loss_file,
            train_loss_graph=django_loss_image
            #train_acc=django_acc_file,
            )
        model.save()
        os.remove(tmp_model_file_path)
        os.remove(tmp_loss_file_path)

    def _create_ctrl_for_normal_dataset(self, algorithm, dataset):
        """
        generates an instance of controller and model
        :param algorithm:
        :param dataset:
        :return:
        """
        from hassbrain_algorithm.controller import Controller
        ctrl = Controller(settings.HASSBRAIN_ALGO_CONFIG) # type: Controller
        dk = self.train_get_ds_type_by_name(dataset.class_name)
        ctrl.set_dataset(dk)
        model_object = self._create_class_from_name(ctrl, algorithm)
        ctrl.load_dataset()
        ctrl.register_model(model_object)
        return ctrl

    def _create_dataset(self, datainstance):
        db_path = self._create_hass_db_path()
        activity_file_path = self._create_activity_file_path(person)
        ctrl = Controller(
            path_to_config=settings.HASSBRAIN_ALGO_CONFIG,
            config={'datasets': { datainstance.name: db_path }}
        )

        params = {'repr': DataRep(datainstance.data_rep),
                  'data_format': 'bernoulli',
                  'test_selection': datainstance.test_sel,
                  'freq': datainstance.timeslicelength}

        ctrl.set_dataset(
            data_name=datainstance.name,
            data_type=Datasettype.HASS,
            params=params
        )

    def _set_custom_act_n_dev(self, ctrl):
        act_list = []
        for act in Activity.objects.all():
            act_list.append(act.name)
        dev_list = []
        for dev in Device.objects.all():
            if dev.location is not None:
                dev_list.append(dev.component.name + "." + dev.name)
        ctrl.set_custom_state_list(act_list)
        ctrl.set_custom_obs_list(dev_list)

    def _create_ctrl_for_hass_instance(self, algorithm, person, datainstance, model_name):
        from hassbrain_algorithm.controller import Controller
        """
        the case where the data should be loaded from the active homeassistant instance
        """
        ctrl = Controller(
            path_to_config=settings.HASSBRAIN_ALGO_CONFIG
        )
        ctrl.load_dataset_from_file(datainstance.data_file)

        model_object = self._create_class_from_name(ctrl, algorithm)
        self._set_custom_act_n_dev(ctrl)
        ctrl.register_model(model_object, model_name)

        #if algorithm.location:
        #    loc_data = AlgorithmView.get_location_data()
        #    ctrl.register_location_info(loc_data)

        #if algorithm.synthetic_activities:
        #    act_data = AlgorithmView.get_activity_data(algorithm.selected_person)
        #    ctrl.register_activity_info(act_data)

        return ctrl

    def _generate_folder_name(self, algorithm, preset_dataset):
        """
        generates a folder in media to store the model file, the visualization and logs in it
        example:
            .. ./media/HMM_chris_homeassistant/
                |-- model.joblib
                |-- visualization.png
                |-- training_loss.csv
        :param algorithm:
        :param hass:
            if hass = True then
        :return:
        """
        algorithm_name = algorithm.name
        dataset_name = algorithm.selected_dataset.name
        if preset_dataset:
            return algorithm_name + "_" + dataset_name
        else:
            person_name = algorithm.selected_person.name
            return person_name + "_" + algorithm_name + "_" + dataset_name

    def _create_media_model_folder_if_not_exists(self, folder_path):
        # if the folder for the person to log the activities to does not exits, create one
        folder_path = settings.MEDIA_ROOT + folder_path
        import os
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def create_model(self, algorithm, model_file, train_acc_file=None, train_loss_file=None, preset_dataset=False):
        from django.core.files.base import File

       # normal
        django_file = File(model_file)
        raise NotImplementedError
        django_file.name = folder_name + "model.joblib"
        print(django_file.name)
        model = Model(
            algorithm=algorithm,
            person=algorithm.selected_person, # can be null
            dataset=algorithm.selected_dataset,
            file=django_file)
        model.save()

    def train_get_ds_type_by_name(self, name):
        from hassbrain_algorithm.controller import Dataset
        dataset_comp = False
        #print('matching datatypes...')
        #print('name: ', name)
        for item in Dataset:
            #print('item: ', item)
            #print('item: ', item.value)
            #print('-')
            if name == item.value:
                dk = item
                dataset_comp = True
                break
        return dk


    def deselect_model(self):
        srv = Server.objects.all()[0]
        algo = srv.selected_algorithm
        algo.selected_dataset = None
        algo.selected_person = None
        algo.save()
        srv.selected_algorithm = None
        srv.save()

    def algo_delete_model(self, model):
        #path_to_model = algo.model.path
        #model = algo.model
        #model.delete()
        algo.save()

        # delete file
        if os.path.isfile(path_to_model):
            os.remove(path_to_model)

    def algo_delete_benchmark(self, algo):
        bench = algo.benchmark
        bench.delete()
        algo.save()

    def delete_selected_model(self):
        model = self.get_sel_model()
        model.delete()

    def evaluate_model(self):
        #algo = self.get_sel_algorithm()
        model = self.get_sel_model()
        dataset = model.dataset
        datainstance = model.datainstance
        person = model.person
        algo = model.algorithm

        md_name = self._create_model_name(algo, person, datainstance)
        # todo find better way to do this
        #if dataset.name == HASS_DB_NAME:
        #    ctrl = self._create_ctrl_for_hass_instance(algo, person, dataset)
        #else:
        #    ctrl = self._create_ctrl_for_normal_dataset(algo, dataset)
        ctrl = self._create_ctrl_for_hass_instance(algo, person, datainstance, md_name)

        file_path = settings.MEDIA_ROOT + model.file.name
        ctrl.load_model(file_path=file_path, name=md_name)
        ctrl.register_benchmark(md_name)

        folder_name = self._generate_folder_name(algorithm=algo, preset_dataset=False)
        tmp_folder_name = 'tmp/' + folder_name

        # bench the model
        reports = ctrl.bench_models()
        MD_INFST_IMG = 'inferred_states.png'
        MD_CONF_MAT = 'confusion_matrix.numpy'
        MD_METRICS = 'metrics.csv'
        MD_CLASS_ACTS = 'class_acts.csv'
        MD_ACT_DUR_DISTS_IMG = 'act_dur_dists.png'
        MD_ACT_DUR_DISTS_DF = 'act_dur_dists.csv'
        DATA_ACT_DUR_DISTS_IMG = 'dataset.act_dur_dists.png'
        DATA_ACT_DUR_DISTS_DF = 'dataset.act_dur_dists.csv'
        MD_FEATURE_IMPORTANCE = 'feature_importance.png'
        fp_dict = {}
        self._create_media_model_folder_if_not_exists(tmp_folder_name)
        fp_dict['df_conf_mat'] = self.get_media_file_path(tmp_folder_name, MD_CONF_MAT)
        fp_dict['df_metrics'] = self.get_media_file_path(tmp_folder_name, MD_METRICS)
        fp_dict['df_class_acts'] = self.get_media_file_path(tmp_folder_name, MD_CLASS_ACTS)
        fp_dict['df_md_act_dur_dists'] = self.get_media_file_path(tmp_folder_name, MD_ACT_DUR_DISTS_DF)
        fp_dict['df_dt_act_dur_dists'] = self.get_media_file_path(tmp_folder_name, DATA_ACT_DUR_DISTS_DF)
        fp_dict['img_inf_states'] = self.get_media_file_path(tmp_folder_name, MD_INFST_IMG)
        fp_dict['img_md_act_dur_dists'] = self.get_media_file_path(tmp_folder_name, MD_ACT_DUR_DISTS_IMG)
        fp_dict['img_dt_act_dur_dists'] = self.get_media_file_path(tmp_folder_name, DATA_ACT_DUR_DISTS_IMG)
        fp_dict['img_fp'] = self.get_media_file_path(tmp_folder_name, MD_FEATURE_IMPORTANCE)

        # save metrics
        ctrl.save_df_metrics_to_file(md_name, fp_dict['df_metrics'])
        ctrl.save_df_confusion(md_name, fp_dict['df_conf_mat'])
        ctrl.save_df_act_dur_dists(md_name, fp_dict['df_md_act_dur_dists'],
                                   fp_dict['df_dt_act_dur_dists'])
        ctrl.save_df_class_accs(md_name, fp_dict['df_class_acts'])
        ctrl.save_plot_inferred_states(md_name, fp_dict['img_inf_states'])
        ctrl.save_plot_act_dur_dists([md_name], fp_dict['img_md_act_dur_dists'])
        ctrl.save_plot_feature_importance(md_name, fp_dict['img_fp'])

        conf_mat = self._create_django_file(fp_dict['df_conf_mat'], folder_name, MD_CONF_MAT)
        metrics = self._create_django_file(fp_dict['df_metrics'], folder_name, MD_METRICS)
        class_acts = self._create_django_file(fp_dict['df_class_acts'], folder_name, MD_CLASS_ACTS)
        fp = self._create_django_img(fp_dict['img_fp'], folder_name, MD_FEATURE_IMPORTANCE)
        act_dur_dists = self._create_django_img(fp_dict['img_md_act_dur_dists'], folder_name, MD_ACT_DUR_DISTS_IMG)
        inf_states = self._create_django_img(fp_dict['img_inf_states'], folder_name, MD_INFST_IMG)

        # save
        bench = Benchmark(
            model=model,
            df_conf_mat=conf_mat,
            df_metrics=metrics,
            df_class_acts=class_acts,
            img_feature_importance=fp,
            img_act_dur_dists=act_dur_dists,
            img_inf_states=inf_states
        )
        bench.save()
        model.save()

    def _create_django_img(self, file_path, folder_name, file_name):
        from django.core.files.images import ImageFile
        django_img_fp = ImageFile(open(file_path, "rb"))
        django_img_fp.name = folder_name + "/" + file_name
        return django_img_fp



    def upload_model(self, request):
        form = ModelForm(request.POST, request.FILES)
        algo = Server.objects.all()[0].selected_algorithm
        person_name = request.POST.get("person_select", "")
        dataset = Dataset.objects.filter(name="homeassistant")[0]

        algo.selected_dataset = dataset
        algo.selected_person = Person.objects.filter(name=person_name)[0]
        algo.save()

        if form.is_valid():
            from django.core.files.base import File

            django_model_file = request.FILES['modelfile']
            folder_name = self._generate_folder_name(algorithm=algo, preset_dataset=False)
            django_model_file.name = folder_name + "/" + MODEL_FILE_NAME
            model = Model(
                algorithm=algo,
                person=algo.selected_person, # can be null
                dataset=algo.selected_dataset,
                file=django_model_file,
                visualization=None,
                train_loss=None,
                train_loss_graph=None
                #train_acc=django_acc_file,
                )
            model.save()




    def get(self, request):
        context = self.create_context(request)
        return render(request, 'algorithms.html', context)

    def post(self, request):
        intent = request.POST.get("intent","")
        if (intent == "select_algorithm"):
            self.select_algorithm(request)

        elif intent == "train_algorithm":
            print('#lalal'*10)
            self.train_algorithm_on_hass_instance(request)

        elif intent == "train_algo_on_preset_dataset":
            print('#JKll'*10)
            self.train_algorithm_on_preset_dataset(request)

        elif intent == "select_model":
            self.select_model(request)

        elif intent == "select_dataset":
            self.select_dataset(request)

        elif intent == "upload_model":
            self.upload_model(request)

        elif intent == "deselect_model":
            self.deselect_model()

        elif intent == "evaluate_algorithm":
            self.evaluate_model()

        elif intent == "delete_model":
            self.delete_selected_model()

        elif intent == "debug":
            #self.debug()
            return self.debug2()

        context = self.create_context(request)
        return render(request, 'algorithms.html', context)


    def debug(self):

        loc_data = self.get_location_data()
        print('#'*100)
        print('loc_data', str(loc_data))


        #print('~'*100)
        #algo = Algorithm(name="asdf")
        #algo.save()

        #bench = Benchmark(algorithm=algo, accuracy=1.2)
        #bench.precision = 1.4
        #bench.f1 = 1.2
        #bench.algorithm = algo
        #bench.save()
        #algo.save()

        #print('~'*10)
        #print(algo)
        #print(bench)
        ## reverse lookup works
        #print(algo.name)
        #print(bench.algorithm.name)
        #print(algo.benchmark.accuracy)
        #print('~'*10)
        #bench.delete()
        #algo.benchmark = None
        #algo.save()
        #print(bench)
        #print(algo.benchmark)

        #algo.benchmark.accuracy = 1.3
        #print(algo.benchmark.accuracy)
        ##algo.delete('benchmark')
        ##bench.delete()
        ##print(bench)
        #print(algo.benchmark)
        #print(bench.pk)

        #print('~'*100)
