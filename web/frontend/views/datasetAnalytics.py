from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
import logging
from django.http import FileResponse
logger = logging.getLogger(__name__)
from frontend.views.dataset import get_datasets_personal_statistics, \
    collect_dataset_statistics, set_placeholder_images, start_plot_gen_service
from frontend.experiment import copy_actfiles2dataset
from frontend.util import collect_data_from_hass

class DatasetAnalyticsView(TemplateView):
    def create_context(self, request):
        srv = get_server()
        context = {}
        dataset = Dataset.objects.get(pk=int(self._getDatasetId(request)))

        context['person_list'] = Person.objects.all()
        context['dataset'] = dataset
        context['ds'] = dataset
        context['person_statistics'] = dataset.person_statistics.all()
        context['datasets_perstats'] = get_datasets_personal_statistics()

        context['service_plot_gen'] = (srv.plot_gen_service_pid is not None)
        return context

    def _getDatasetId(self, request):
        """ extracts the id of the  dataset from the url
        """
        if request.get_full_path().split("/")[-1] == "":
            return int(request.get_full_path().split("/")[-2])
        else:
            return int(request.get_full_path().split("/")[-1])

    def generate_analysis(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)

        srv = get_server()
        if srv.dataset is not None and srv.dataset.id == ds.id: 
            copy_actfiles2dataset(ds)
            collect_data_from_hass()
        collect_dataset_statistics(ds)
        set_placeholder_images(ds)
        start_plot_gen_service(ds)

    def post(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['generate_analysis']
        if intent == 'generate_analysis':
            self.generate_analysis(request)

        context = self.create_context(request)
        return render(request, 'dataset_analytics.html', context)

    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset_analytics.html', context)