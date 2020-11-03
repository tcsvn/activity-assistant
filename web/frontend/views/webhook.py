from backend.models import *
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
from django.http import JsonResponse
from django.views.generic import TemplateView
from pyadlml.dataset._datasets.homeassistant import hass_db_2_data
from pyadlml.dataset._datasets.activity_assistant import _read_devices
import pandas as pd
from backend.serializers import DatasetSerializer
from frontend.util import get_device_names, load_data_file, \
    load_device_mapping
from pyadlml.dataset import DEVICE

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
        from frontend.util import hass_db_2_data
        df_new = hass_db_2_data(DB_URL, get_device_names())\
                    .drop_duplicates()

        df_cur = load_data_file(ds.path_to_folder)

        df = pd.concat([df_cur, df_new], ignore_index=True)

        # save df
        dev_map = load_device_mapping(ds.path_to_folder, as_dict=True)
        df[DEVICE] = df[DEVICE].map(dev_map)
        df = df.drop_duplicates()
        df.to_csv(ds.path_to_folder + 'devices.csv', sep=',', index=False)

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