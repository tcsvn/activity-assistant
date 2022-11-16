from backend.models import Device, Dataset, Person
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server
import logging
from django.http import FileResponse
logger = logging.getLogger(__name__)
from frontend.util import collect_data_from_hass
from hass_api.rest import HARest
from pyadlml.constants import DEVICE
from pyadlml.dataset import load_act_assist

class DatasetAnalyticsView(TemplateView):
    def create_context(self, request):

        srv = get_server()
        context = {}
        dataset = Dataset.objects.get(pk=int(self._getDatasetId(request)))


        from .datasetAnalyticsPlotly import build_app
        data = load_act_assist(dataset.path_to_folder)

        df_devs = data['df_devices']

        # Replace device names with friendly names from Home Assistant
        mapping = Device.get_friendly_name_mapping(
            name_list=df_devs[DEVICE].unique(),
            names_as_key=True,
        ) 
        df_devs[DEVICE] = df_devs[DEVICE].map(mapping)

        build_app(data['df_activities'], df_devs, name=dataset.name)

        context['person_list'] = Person.objects.all()
        context['dataset'] = dataset
        context['ds'] = dataset

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

    
    # TODO refactor, mark for deletion
    #def export_data(self, request):
    #    name = request.POST.get("dataset_name","")
    #    ds = Dataset.objects.get(name=name)
    #    srv = get_server()

    #    try:
    #        if ds.id == srv.dataset.id:
    #            copy_actfiles2dataset(ds)
    #            collect_data_from_hass()
    #    except AttributeError:
    #        pass

    #    return ds.get_fileResponse()

    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset_analytics.html', context)