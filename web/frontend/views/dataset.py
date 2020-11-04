from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names, \
    pause_experiment, continue_experiment, finish_experiment

# css frontend
class DatasetView(TemplateView):
    # list all persons and render them into the frontend
    def create_context(self, request):
        context = {}
        context['person_list'] = Person.objects.all()
        context['dataset_list'] = Dataset.objects.all()
        srv = get_server()
        if srv.dataset is not None:
            context['dataset'] = srv.dataset
            context['experiment_running'] = True
            context['polling'] = srv.is_polling
        else:
            context['experiment_running'] = False
            dev_lst = get_device_names()
            context['device_lst'] = dev_lst
            context['num_devs'] = len(dev_lst)
        return context

    def delete_dataset(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)
        path = ds.path_to_folder
        import shutil
        shutil.rmtree(path)
        ds.delete()

    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

    def post(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['pause_experiment', 'continue_experiment', 'finish_experiment',
         'delete_dataset', 'export_data']
        if intent == 'pause_experiment':
            pause_experiment()
        elif intent == 'continue_experiment':
            continue_experiment()
        elif intent == 'finish_experiment':
            finish_experiment()
        elif intent == 'delete_dataset':
            self.delete_dataset(request)
        elif intent == 'delete_dataset':
            self.export_data(request)
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

