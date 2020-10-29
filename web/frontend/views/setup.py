from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

import os 
import homeassistant_api.rest as hass_rest
from frontend.util import get_device_by_id, get_server, get_device_names, get_activity_names
"""
this view connects to homeassistant and gets all the relevant data to 
setup activity assistant
"""
SETUP_STEPS = ["step 0", "step 1", "step 2", "step 3", "step 4", "completed"]

class SetupView(TemplateView):

    def create_context(self):
        srv = get_server()
        if srv.setup is None:
            srv.setup = SETUP_STEPS[0]
            srv.save()
        index = SETUP_STEPS.index(srv.setup)
        progress = round((index/len(SETUP_STEPS))*100, 2)

        context = {
            'step':srv.setup,
            'progress':progress
        }
        if srv.setup == SETUP_STEPS[2]:
            hass_devices = hass_rest.get_device_list(
                settings.HASS_API_URL , srv.hass_api_token)
            devices = Device.objects.all()
            dev_list = []
            for dev in devices:
                dev_list.append(dev.name)
            hass_devices = list(set(hass_devices).difference(set(dev_list)))
            context['hass_dev_list'] = hass_devices
            context['aa_dev_list'] = get_device_names()
        elif srv.setup == SETUP_STEPS[3]:
            context['activity_list'] = Activity.objects.all()
        elif srv.setup == SETUP_STEPS[4]:
            hass_users = hass_rest.get_user_names(
                settings.HASS_API_URL, srv.hass_api_token,
            )
            aa_users = []
            for u in Person.objects.all():
                aa_users.append(u.name)
            hass_users = list(set(hass_users).difference(set(aa_users)))
            context['hass_user_list'] = hass_users
            context['aa_user_list'] = Person.objects.all()
            write_to_srv_poll_int(hass_users)
        return context

    def _increment_one_step(self):
        srv = get_server()
        index = SETUP_STEPS.index(srv.setup)
        srv.setup = SETUP_STEPS[index+1]
        srv.save()


    def post_step0(self, request):
        """ reads api key from environment 
            gets outside url 
            gets path to database
            and pings the activity assistant component
        """
        # get rest api key
        srv = get_server()
        srv.hass_api_token = os.environ.get('SUPERVISOR_TOKEN')
        srv.save()

        # get server_address
        disc_url = settings.HASS_API_URL + '/discovery_info'
        tmp = hass_rest.get(disc_url, srv.hass_api_token)
        srv.server_address = tmp['base_url']
        srv.save()
        self._increment_one_step()

    def post_step1(self, request):
        p_int = str(request.POST.get("poll_interval", ""))
        assert p_int in ['30s', '1m', '5m', '10m', '30m', '1h', '2h', '6h']
        srv = get_server()
        srv.poll_interval = p_int
        srv.save()
        self._increment_one_step()

    def post_step2(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['track', 'remove', 'next_step']
        dev_lst = request.POST.getlist('devices')
        if intent == 'track':
            for name in request.POST.getlist('hass_select'):
                Device(name=name).save()
        elif intent == 'remove':
            for name in request.POST.getlist('act_assist_select'):
                Device.objects.get(name=name).delete()
        else:
            self._increment_one_step()

    def post_step3(self, request):
        intent = request.POST.get("intent", "")
        assert intent in ['add', 'delete', 'next_step']
        if intent == 'delete':
            for name in request.POST.getlist('act_select'):
                Activity.objects.get(name=name).delete()
        elif intent == 'add':
            name = request.POST.get("name", "")
            if name not in get_activity_names():
                Activity(name=name).save()
        else:
            self._increment_one_step()

    def post_step4(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['track', 'remove', 'next_step', 'add']
        dev_lst = request.POST.getlist('devices')
        if intent == 'track':
            for hass_name in request.POST.getlist('hass_select'):
                name = hass_name.split('.')[0]
                Person(name=name, hass_name=hass_name).save()
        elif intent == 'remove':
            for col in request.POST.getlist('act_assist_select'):
                name = col.split(' ')[0]
                Person.objects.get(name=name).delete()
        elif intent == 'add':
            name = request.POST.get("name", "")
            Person(name=name, hass_name='person.' + name).save()
        else:
            self._increment_one_step()

    def post(self, request):
        from_step = request.POST.get("from_step","")
        if from_step == SETUP_STEPS[0]:
            self.post_step0(request)
        elif from_step == SETUP_STEPS[1]:
            self.post_step1(request)
        elif from_step == SETUP_STEPS[2]:
            self.post_step2(request)
        elif from_step == SETUP_STEPS[3]:
            self.post_step3(request)
        elif from_step == SETUP_STEPS[4]:
            self.post_step4(request)
        else:
            return return_var(str(request)) 
        context = self.create_context()
        return render(request, 'setup.html', context)

    # list all persons and render them into the frontend
    def get(self, request):
        srv = Server.objects.all()[0]
        if srv.setup == "completed":
            return redirect('/dashboard/')
        else:
            context = self.create_context()
            return render(request, 'setup.html', context)

def return_var(var):
    from django.http import HttpResponse
    msg = f'Today is {var}'
    return HttpResponse(msg, content_type='text/plain')


def write_to_srv_poll_int(var):
    srv = get_server()
    srv.poll_interval = str(var) 
    srv.save()