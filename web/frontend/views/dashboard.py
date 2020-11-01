from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import *

class DashboardView(TemplateView):


    def is_rt_node_running(self):
        srv = Server.objects.all()[0]
        try:
            return srv.realtime_node is not None
        except:
            return False

    def create_context(self):
        person_list = Person.objects.all()
        device_list = Device.objects.all()
        activity_list = Activity.objects.all()
        count_person = len(person_list)
        #count_models = len(Model.objects.all())
        count_models = 0
        count_activity = len(activity_list)
        count_device = len(Device.objects.all())
        srv = get_server()
        setup_complete = srv.setup == 'complete'
        experiment_stat = get_experiment_status()
        is_exp_active = is_experiment_active()
        #rt_node_running = self.is_rt_node_running()
        #rt_node = srv.realtime_node
        #model_list = Model.objects.all()
        context = {
            'person_list' : person_list,
            #'model_list' : model_list,
            'activity_list' : activity_list,
            'count_person' : count_person,
            'count_models' : count_models,
            'count_activity' : count_activity,
            'count_device' : count_device,
            'setup_complete' : setup_complete,
            'experiment_status':experiment_stat,
            'experiment_active': is_exp_active,
            #'rt_node_running' : rt_node_running,
            #'rt_node' : rt_node
        }
        if is_exp_active:
            context['dataset'] = srv.dataset
        return context


    def run(self, request):
        srv = Server.objects.all()[0]
        model_pk = request.POST.get("model_select","")
        model = Model.objects.filter(pk=model_pk)[0]

        # open the script
        hassbrain_url = srv.server_address
        # todo load user instead of string
        HASSBRAIN_USER = "admin"
        HASSBRAIN_PW = "asdf"

        import subprocess
        proc = subprocess.Popen([
            "python", settings.HASSBRAIN_PATH_TO_RT_MAIN,
            "--host", hassbrain_url,
            "-u", HASSBRAIN_USER,
            "-p", HASSBRAIN_PW
        ],
            close_fds=True
        )
        rt = RealTimeNode(pid=proc.pid, status="alive", model=model)
        #rt = RealTimeNode(pid=1234, status="alive", model=model)
        rt.save()
        srv.realtime_node = rt
        srv.save()

    def stop(self):
        import os
        import signal
        rt_node = Server.objects.all()[0].realtime_node
        try:
            os.kill(rt_node.pid, signal.SIGTERM)
            # todo leaves zombie behind correct this by sigterm handling in async io node
        except ProcessLookupError:
            print('process allready deleted')
        #import psutil

        #current_process = psutil.Process()
        #children = current_process.children(recursive=True)
        #for child in children:
        #    print('Child pid is {}'.format(child.pid))
        rt_node.delete()

    def start_experiment(self, request):
        """ creates a new dataset object and assigns it to the server
            that it knows an experiment is running. Also creates folders
            like 
                media/dataset/<datasetname>/<person_activities.csv>
                media/dataset/<datasetname>/data.csv
                ...
            
        """
        ds_name = request.POST.get("name","")
        try:
            Dataset.objects.get(name=ds_name)
            return
        except:
            pass

        # 1. create dataset 
        dataset_folder = settings.DATASET_PATH + ds_name +'/'
        ds = Dataset(name=ds_name, logging=True, path_to_folder=dataset_folder)
        ds.save()
        # 
        srv = get_server()
        srv.dataset = ds
        srv.save()

        # 2. create folders and inital files
        from pathlib import Path
        from frontend.util import create_device_mapping_file, \
            create_activity_files, create_data_file

        Path(ds.path_to_folder).mkdir(mode=0o777, parents=True, exist_ok=False)
        create_data_file(ds.path_to_folder)
        create_activity_files(ds.path_to_folder, Person.objects.all()) 
        create_device_mapping_file(ds.path_to_folder) 

        # TODO save prior information about persons
        # TODO save room assignments of sensors and activities

        # 3. tell HASS component to start logging

    def pause_experiment(self):
        """ indicates to pause logging on AA level and send a message to 
            the HASS component to stop the webhook sendings
        """
        ds = get_server().dataset
        ds.logging = False
        ds.save()

        # TODO communicate to HASS component

    def continue_experiment(self):
        ds = get_server().dataset
        ds.logging = True
        ds.save()   
        # TODO communicate to HASS component

    def finish_experiment(self):
        srv = get_server()
        ds = srv.dataset
        srv.dataset = None
        srv.save()
        ds.logging = False
        from django.utils.timezone import now
        ds.end_time = now()
        ds.save()
        # TODO remove debug line below
        ds.delete()
        # TODO tell HASS component to stop logging

    def post(self, request):
        intent = request.POST.get("intent","")
        if intent == "run rt_node":
            self.run(request)
        elif intent == "stop rt_node":
            self.stop()
        elif intent == "start experiment":
            self.start_experiment(request)
        elif intent == "pause experiment":
            self.pause_experiment()
        elif intent == "continue experiment":
            self.continue_experiment()
        elif intent == "finish experiment":
            self.finish_experiment()
        context = self.create_context()
        return render(request, 'dashboard.html', context)

    def get(self, request):
        context = self.create_context()
        return render(request, 'dashboard.html', context)