from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
# css frontend
class DatasetView(TemplateView):
    # list all persons and render them into the frontend
    def create_context(self, request):
        context = {}
        srv = get_server()
        if srv.dataset is not None:
            context['dataset'] = srv.dataset
            context['experiment_running'] = True
        else:
            context['experiment_running'] = False
            dev_lst = get_device_names()
            context['device_lst'] = dev_lst
            context['num_devs'] = len(dev_lst)
        return context

    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset.html', context)


    def start_experiment(self):
        """ creates an initial dataset and assigns it as active to a server
        """
        srv = get_server()
        logging = False
        path_to_folder = '/home/blas'
        ds = Dataset(logging=logging, path_to_folder=path_to_folder)
        ds.save()
        srv.dataset = ds
        srv.save()

    def post(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['start_experiment']
        if intent == 'start_experiment':
            self.start_experiment()
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

