from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
import logging
from django.http import FileResponse
logger = logging.getLogger(__name__)
from frontend.views.dataset import get_datasets_personal_statistics

class DatasetAnalyticsView(TemplateView):
    def create_context(self, request):
        context = {}
        dataset = Dataset.objects.get(pk=int(self._getDatasetId(request)))

        context['person_list'] = Person.objects.all()
        context['dataset'] = dataset
        context['ds'] = dataset
        context['person_statistics'] = dataset.person_statistics.all()
        context['datasets_perstats'] = get_datasets_personal_statistics()
        return context

    def _getDatasetId(self, request):
        """ extracts the id of the  dataset from the url
        """
        if request.get_full_path().split("/")[-1] == "":
            return int(request.get_full_path().split("/")[-2])
        else:
            return int(request.get_full_path().split("/")[-1])


    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset_analytics.html', context)