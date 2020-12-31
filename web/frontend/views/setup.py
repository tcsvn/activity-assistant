from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

import os 
import hass_api.rest as hass_rest
from frontend.util import get_server, start_zero_conf_server,\
    get_device_names, get_activity_names, get_person_names,\
    stop_zero_conf_server, refresh_hass_token, get_person_hass_names

from frontend.views.config import conf_devices, conf_activities, conf_persons
import logging
logger = logging.getLogger(__name__)


"""
this view connects to homeassistant and gets all the relevant data to 
setup activity assistant
"""
SETUP_STEPS = ["step 0", "step 1", "conf_devices", "conf_activities",
                 "conf_persons", "step 5", "completed"]

class SetupView(TemplateView):

    def create_context(self):
        srv = get_server()
        if srv.setup is None:
            srv.setup = SETUP_STEPS[0]
            srv.save()
        index = SETUP_STEPS.index(srv.setup)
        progress = round((index/(len(SETUP_STEPS)-2))*100, 2)

        context = {
            'step':srv.setup,
            'progress':progress,
            'url':'setup'
        }
        if srv.setup == SETUP_STEPS[0]:
            start_zero_conf_server()
        if srv.setup == SETUP_STEPS[1]:
            context['poll_int_list'] = settings.POLL_INTERVAL_LST
        elif srv.setup == SETUP_STEPS[2]:
            hass_devices = hass_rest.get_device_list(
                settings.HASS_API_URL , srv.hass_api_token)

            dev_list = get_device_names()
            hass_devices = list(set(hass_devices).difference(set(dev_list)))

            context['hass_dev_list'] = hass_devices
            context['aa_dev_list'] = get_device_names()
        elif srv.setup == SETUP_STEPS[3]:
            context['activity_list'] = Activity.objects.all()
        elif srv.setup == SETUP_STEPS[4]:
            hass_users = hass_rest.get_user_names(
                settings.HASS_API_URL, srv.hass_api_token,
            )
            hass_users = list(set(hass_users).difference(set(get_person_hass_names())))
            context['hass_user_list'] = hass_users
            context['aa_user_list'] = Person.objects.all()
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
        refresh_hass_token()

        # get server_address
        srv = get_server()
        disc_url = settings.HASS_API_URL + '/discovery_info'
        tmp = hass_rest.get(disc_url, srv.hass_api_token)
        srv.server_address = tmp['base_url']

        srv.time_zone = hass_rest.get_time_zone(
            settings.HASS_API_URL,
            srv.hass_api_token
        )

        srv.save()

        # only advance if the component was installed at hass site
        #if srv.hass_comp_installed:
        stop_zero_conf_server()
        #self._increment_one_step()
        


    def post_step1(self, request):
        """ select poll interval
        """
        p_int = str(request.POST.get("poll_interval", ""))
        assert p_int in settings.POLL_INTERVAL_LST
        srv = get_server()
        srv.poll_interval = p_int
        srv.save()
        self._increment_one_step()

    def post_step2(self, request):
        """ select devices to track
        """
        intent = request.POST.get("intent","")
        assert intent in ['track', 'remove', 'next_step']

        if intent == 'next_step':
            self._increment_one_step()
        else:
            conf_devices(request)

    def post_step3(self, request):
        """ create activities
        """
        intent = request.POST.get("intent", "")
        assert intent in ['add', 'delete', 'next_step']
        if intent == 'next_step':
            self._increment_one_step()
        else:
            conf_activities(request)

    def post_step4(self, request):
        """ track persons
        """
        intent = request.POST.get("intent","")
        assert intent in ['track', 'remove', 'next_step', 'add']
        if intent == 'next_step':
            self._increment_one_step()
        else:
            conf_persons(request)

    def post(self, request):
        from_step = request.POST.get("from","")
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
        elif from_step == SETUP_STEPS[5]:
            self._increment_one_step()
            return redirect('/dashboard/')
        else:
            return return_var(str(request.POST)) 
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