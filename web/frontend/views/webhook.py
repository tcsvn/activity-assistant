from backend.models import *
from django.shortcuts import render, redirect
from frontend.util import get_server
from django.http import JsonResponse
from django.views.generic import TemplateView
from backend.serializers import DatasetSerializer
from frontend.util import collect_data_from_hass
import frontend.experiment as experiment

class WebhookView(TemplateView):
    def enable_hass_comp(self):
        srv = get_server()
        srv.hass_comp_installed = True
        srv.save()
        
    def get(self, request):
        srv = get_server()
        srv.webhook_count += 1
        srv.save()
        if not srv.hass_comp_installed:
            self.enable_hass_comp()
            resp = {'state':'success'}
        elif srv.experiment_status() == "running":
            collect_data_from_hass()
            resp = {'state':''}
        else:
            resp = {}
        return JsonResponse(resp)

    def post(self, request):
        resp = {}
        return JsonResponse(resp)