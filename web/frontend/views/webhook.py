from backend.models import *
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
from django.http import JsonResponse
from django.views.generic import TemplateView
from pyadlml.dataset._datasets.homeassistant import hass_db_2_data
from pyadlml.dataset._datasets.activity_assistant import _read_devices
import pandas as pd
from backend.serializers import DatasetSerializer
from frontend.util import get_device_names

# todo somehow get this dynamically
DB_URL = 'sqlite:////config/home-assistant_v2.db' 

class WebhookView(TemplateView):
    def enable_hass_comp(self):
        srv = get_server()
        srv.hass_comp_installed = True
        srv.save()





    def collect_data_from_hass(self):
        # this is the case where the data is pulled
        srv = get_server()
        ds = srv.dataset
        ds.path_to_folder
        df_new = hass_db_2_data(DB_URL, get_device_names())

        # load df
        #df_cur = _read_devices(ds.path_to_folder + settings.DATA_FILE_NAME,
        #            ds.path_to_folder + setting.DATA_MAPPING_FILE_NAME)
        #df_cur = pd.read_csv()


        # merge df

        # save df
        #df.to_csv()

    def get(self, request):
        srv = get_server()
        if not srv.hass_comp_installed:
            self.enable_hass_comp()
            resp = {'state':'success'}
        else:
            if True:
            #try:
                resp = {'state':str(self.collect_data_from_hass())}
            #except:
            #    resp = {'state':'failure'}
        return JsonResponse(resp)

    def post(self, request):
        resp = {}
        return JsonResponse(resp)