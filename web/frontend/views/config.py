from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
import os 
import hass_api.rest as hass_rest
from frontend.util import get_server, is_experiment_active,\
    get_device_names, get_activity_names, get_person_names 


class ConfigView(TemplateView):
    def get_context(self):
        srv = get_server()
        person_list = Person.objects.all()
        act_list = Activity.objects.all()
        url = 'config'
        exp_active = is_experiment_active()

        # get hass devices
        hass_devices = hass_rest.get_device_list(
            settings.HASS_API_URL , srv.hass_api_token)
        dev_list = get_device_names()
        hass_devices = list(set(hass_devices).difference(set(dev_list)))


        # get hass users
        hass_users = hass_rest.get_user_names(
            settings.HASS_API_URL, srv.hass_api_token,)
        hass_users = list(set(hass_users).difference(set(get_person_names())))

        return {'server': srv,
                'url': url,
                'person_list':person_list,
                'hass_dev_list' : hass_devices,
                'aa_dev_list' : dev_list,
                'activity_list' : act_list,
                'hass_user_list' : hass_users,
                'aa_user_list' : person_list, 
                'poll_int_list' : settings.POLL_INTERVAL_LST,
                'experiment_active':exp_active,
                }

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, 'config.html', context)

    def post(self, request):
        from_section = request.POST.get("from", "")
        assert from_section in ["conf_devices", "conf_persons", "conf_activities", "conf_server"]
        if from_section == 'conf_devices': 
            conf_devices(request)
        elif from_section == 'conf_persons': 
            conf_persons(request)
        elif from_section == 'conf_activities': 
            conf_activities(request)
        else:
            conf_server(request)

        context = self.get_context()
        return render(request, 'config.html', context)

def conf_server(request):
    srv = get_server()
    try:
        is_polling = request.POST.get("is_polling", "")
        if is_polling == 'on':
            srv.is_polling = True
        else:
            srv.is_polling = False
    except:
        pass
    try:
        pol_int = request.POST.get("poll_interval", "")
        srv.poll_interval = pol_int
    except: 
        pass
    try:
        address = request.POST.get("address", "")
        if address != '':
            srv.server_address = address
    except:
        pass
    srv.save()

def conf_devices(request):
    intent = request.POST.get("intent","")
    assert intent in ['track', 'remove']
    dev_lst = request.POST.getlist('devices')
    if intent == 'track':
        for name in request.POST.getlist('hass_select'):
            Device(name=name).save()
    else:
        for name in request.POST.getlist('act_assist_select'):
            Device.objects.get(name=name).delete()

def conf_activities(request):
    intent = request.POST.get("intent", "")
    assert intent in ['add', 'delete']
    if intent == 'delete':
        for name in request.POST.getlist('act_select'):
            Activity.objects.get(name=name).delete()
    else:
        name = request.POST.get("name", "")
        if name not in get_activity_names():
            Activity(name=name).save()

def conf_persons(request):
    intent = request.POST.get("intent","")
    assert intent in ['track', 'remove', 'add']
    dev_lst = request.POST.getlist('devices')
    if intent == 'track':
        for hass_name in request.POST.getlist('hass_select'):
            name = hass_name.split('.')[1]
            Person(name=name, hass_name=hass_name).save()
    elif intent == 'remove':
        for col in request.POST.getlist('act_assist_select'):
            name = col.split(' ')[0]
            Person.objects.get(name=name).delete()
    else:
        name = request.POST.get("name", "")
        Person(name=name, hass_name='person.' + name).save()
