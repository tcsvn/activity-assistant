from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
import os 
import hass_api.rest as hass_rest
from frontend.util import get_server, refresh_hass_token, \
    get_device_names, get_activity_names, get_person_hass_names, \
    get_person_names, input_is_empty
import frontend.experiment as experiment

LOCAL_URL_PROVIDED = 'server_local_url_provided'
INVALID_ADDRESS_PROVIDED = 'server_invalid_address_provided'

class ConfigView(TemplateView):
    def get_context(self, add_to_context):
        srv = get_server()
        person_list = Person.objects.all()
        act_list = Activity.objects.all()
        url = 'config'
        exp_active = experiment.is_active()
        refresh_hass_token()

        # get hass devices
        hass_devices = hass_rest.get_device_list(
            settings.HASS_API_URL , srv.hass_api_token)
        dev_list = get_device_names()
        hass_devices = list(set(hass_devices).difference(set(dev_list)))


        # get hass users
        hass_users = hass_rest.get_user_names(
            settings.HASS_API_URL, srv.hass_api_token,)

        hass_users = list(set(hass_users).difference(set(get_person_hass_names())))
        context = {'server': srv,
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
        context.update(add_to_context)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context({})
        return render(request, 'config.html', context)

    def post(self, request):
        from_section = request.POST.get("from", "")
        add_to_context = {}
        assert from_section in ["conf_devices", "conf_persons",\
             "conf_activities", "conf_server", "debug"]
        if from_section == 'conf_devices': 
            conf_devices(request)
        elif from_section == 'conf_persons': 
            conf_persons(request)
        elif from_section == 'conf_activities': 
            conf_activities(request)
        elif from_section == 'conf_server':
            success, reason = conf_server(request)
            if not success and reason:
                add_to_context[reason] = True
            if not success and reason:
                add_to_context[reason] = True


        elif from_section == 'debug':
            debug(request)

        context = self.get_context(add_to_context)
        return render(request, 'config.html', context)

def debug(request):
    from frontend.util import collect_data_from_hass
    collect_data_from_hass()

def conf_server(request):
    """ sets server related stuff
    """
    logger.error('test')
    srv = get_server()
    try:
        pol_int = request.POST.get("poll_interval", "")
        srv.poll_interval = pol_int
    except: 
        pass

    srv.save()
    try:
        address = request.POST.get("address", "")
        if input_is_valid_address(address):
            if input_is_local_address(address):
                return False, LOCAL_URL_PROVIDED
            address = url_strip_appendix(address)
            srv.server_address = address
            srv.save()
            return (True, None)
        else:
            return False, INVALID_ADDRESS_PROVIDED
    except:
        return (True, None)

def url_strip_appendix(url):
    """ removes trailing stuff behind a url definition
    """
    lst = url.split('/')
    return lst[0] + '//' + lst[2]

def input_is_valid_address(address):
    """ checks whether the given address is either a valid ipv4 or a valid url
    """
    from django.core.validators import URLValidator
    try:
        URLValidator()(address)
        return True
    except:
        return False

def input_is_local_address(address):
    return '.local' in address

def conf_devices(request):
    intent = request.POST.get("intent","")
    assert intent in ['track', 'remove']
    dev_lst = request.POST.getlist('devices')
    if intent == 'track':
        lst = request.POST.getlist('hass_select')
        if len(lst) == 1 and input_is_empty(lst[0]):
            return
        for name in lst:
            Device(name=name).save()
    else:
        lst = request.POST.getlist('act_assist_select')
        if len(lst) == 1 and input_is_empty(lst[0]):
            return
        for name in lst:
            Device.objects.get(name=name).delete()

def conf_activities(request):
    intent = request.POST.get("intent", "")
    assert intent in ['add', 'delete']
    if intent == 'delete':
        for name in request.POST.getlist('act_select'):
            Activity.objects.get(name=name).delete()
    else:
        name = request.POST.get("name", "")
        if name not in get_activity_names() and not input_is_empty(name):
            Activity(name=name).save()

def conf_persons(request):
    intent = request.POST.get("intent","")
    assert intent in ['track', 'remove', 'add']
    dev_lst = request.POST.getlist('devices')
    if intent == 'track':
        lst = request.POST.getlist('hass_select')
        if len(lst) == 1 and input_is_empty(lst[0]):
            return
        for hass_name in lst:
            name = hass_name.split('.')[1]
            Person(name=name, hass_name=hass_name).save()
    elif intent == 'remove':
        lst = request.POST.getlist('act_assist_select')
        if len(lst) == 1 and input_is_empty(lst[0]):
            return
        for col in lst:
            name = col.split(' ')[0]
            Person.objects.get(name=name).delete()
    else:
        name = request.POST.get("name", "")
        if name not in get_person_names() and not input_is_empty(name):
            Person(name=name, hass_name='person.' + name).save()
