from backend.models import *
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
from django.http import JsonResponse
from django.views.generic import TemplateView
from pyadlml.dataset._datasets.homeassistant import hass_db_2_data
from pyadlml.dataset._datasets.activity_assistant import _read_devices
import pandas as pd
from backend.serializers import DatasetSerializer
from frontend.util import get_device_names, load_data_file

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
        def hass_db_2_data(url, device_list):
            import pandas
            import sqlalchemy
            engine = sqlalchemy.create_engine(DB_URL)
            df = pandas.read_sql("SELECT * FROM persons", con = engine)
            limiit =5000000
            query = f"""
            SELECT entity_id, state, last_changed
            FROM states
            WHERE
                state NOT IN ('unknown', 'unavailable')
            ORDER BY last_changed DESC
            LIMIT {limit}
            """
            df = pd.read_sql_query(query, db_url)

        df_new = hass_db_2_data(DB_URL, get_device_names())

        # load df
        df_dev = load_data_file(ds.path_to_folder)
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