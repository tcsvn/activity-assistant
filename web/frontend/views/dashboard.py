from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import *
from pathlib import Path
import frontend.experiment as experiment
import os
import signal

class DashboardView(TemplateView):

    def is_rt_node_running(self):
        srv = Server.objects.all()[0]
        try:
            return srv.realtime_node is not None
        except:
            return False

    def create_context(self, add_context=None):
        """
        Parameters
        ----------
        add_context : dict
            additional context to set to the normal one
        """
        person_list = Person.objects.all()
        device_list = Device.objects.all()
        activity_list = Activity.objects.all()
        dataset_list = Dataset.objects.all()
        count_person = len(person_list)
        #count_models = len(Model.objects.all())
        count_models = 0
        count_activity = len(activity_list)
        count_device = len(device_list)
        count_dataset = len(dataset_list)
        srv = get_server()
        setup_complete = srv.setup == 'complete'
        experiment_stat = experiment.get_status()
        is_exp_active = experiment.is_active()
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
            'count_dataset' : count_dataset,
            'setup_complete' : setup_complete,
            'experiment_status':experiment_stat,
            'experiment_active': is_exp_active,
            #'rt_node_running' : rt_node_running,
            #'rt_node' : rt_node
        }
        if is_exp_active:
            context['dataset'] = srv.dataset
        if add_context is not None:
            context.update(add_context)
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



    def post(self, request):
        intent = request.POST.get("intent","")
        add_context = {}
        if intent == "run rt_node":
            self.run(request)
        elif intent == "stop rt_node":
            self.stop()
        elif intent == "start experiment":
            if not experiment.start(request):
                add_context['exp_duplicate_names'] = True
            else:
                add_context['started_experiment'] = True
        elif intent == "pause experiment":
            experiment.pause()
        elif intent == "continue experiment":
            experiment.resume()
        elif intent == "finish experiment":
            experiment.finish()
        context = self.create_context(add_context)
        return render(request, 'dashboard.html', context)

    def get(self, request):
        context = self.create_context()
        return render(request, 'dashboard.html', context)