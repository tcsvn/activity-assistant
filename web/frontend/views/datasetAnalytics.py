from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server
import logging
from django.http import FileResponse
logger = logging.getLogger(__name__)
from frontend.util import collect_data_from_hass

class DatasetAnalyticsView(TemplateView):
    def create_context(self, request):

        srv = get_server()
        context = {}
        dataset = Dataset.objects.get(pk=int(self._getDatasetId(request)))


        from .datasetAnalyticsPlotly import build_app
        from pyadlml.dataset import load_act_assist
        data = load_act_assist(dataset.path_to_folder)

        build_app(data['df_activities_admin'], data['df_devices'], name=dataset.name)

        context['person_list'] = Person.objects.all()
        context['dataset'] = dataset
        context['ds'] = dataset
        #context['person_statistics'] = dataset.person_statistics.all()    TODO refactor
        #context['datasets_perstats'] = get_datasets_personal_statistics() TODO refactor

        context['service_plot_gen'] = (srv.plot_gen_service_pid is not None)

        tmp = dataset.get_persons_from_folder()
        context['dash_context'] = dict(
            act_assist_path=dict(value=dataset.path_to_folder),
            subject_names=dict(value=tmp)
        )

        return context

    def _getDatasetId(self, request):
        """ extracts the id of the  dataset from the url
        """
        if request.get_full_path().split("/")[-1] == "":
            return int(request.get_full_path().split("/")[-2])
        else:
            return int(request.get_full_path().split("/")[-1])

    
    def export_data(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)
        srv = get_server()

        try:
            if ds.id == srv.dataset.id:
                copy_actfiles2dataset(ds)
                collect_data_from_hass()
        except AttributeError:
            pass

        return ds.get_fileResponse()


    #def post(self, request):
    #    intent = request.POST.get("intent","")
    #    assert intent in ['export_dataset']
    #    if intent == 'export_dataset':
    #        return self.export_data(request)

    #    context = self.create_context(request)
    #    return render(request, 'dataset_analytics.html', context)

    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset_analytics.html', context)