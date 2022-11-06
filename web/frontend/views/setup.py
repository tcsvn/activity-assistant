from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

import os 
import hass_api.rest as hass_rest
from hass_api.rest import HARest, HASup
from frontend.util import get_server, ping_db

from frontend.views.config import conf_devices, conf_activities, conf_persons
import logging
logger = logging.getLogger(__name__)


"""
this view connects to homeassistant and gets all the relevant data to 
setup activity assistant
"""
SETUP_STEPS = ["initial", "data_collection", "conf_devices", "conf_activities",
                 "conf_persons", "final", "completed"]

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
            self.get_step0(context)

        if srv.setup == SETUP_STEPS[1]:
            self.get_step1(context)

        elif srv.setup == SETUP_STEPS[2]:
            self.get_step2(context)

        elif srv.setup == SETUP_STEPS[3]:
            self.get_step3(context)

        elif srv.setup == SETUP_STEPS[4]:
            self.get_step4(context)

        return context


    def _increment_one_step(self):
        srv = get_server()
        index = SETUP_STEPS.index(srv.setup)
        srv.setup = SETUP_STEPS[index+1]
        srv.save()


    def get_step0(self, context):
        pass
        
 
    def get_step1(self, context):
        srv = get_server()
        context['poll_int_list'] = settings.POLL_INTERVAL_LST
        # mysql-client
        from frontend.hass_db import url_from_hass_config
        try: 
            url, db_type = url_from_hass_config('/config')
            logger.error('url: ' + str(url) )
            ping_db(url)
            context['hass_db_success'] = True
            srv.hass_db_url = url
            srv.save()
        except Exception as e:
            logger.error('Exception catched: ' + str(e))
            context['hass_db_success'] = False
            context['error_text'] = e
        context['db_type'] = db_type


    
    def get_step2(self, context):
        hres = HARest()
        hass_devices = hres.get_device_list()

        dev_list = Device.get_all_names()
        hass_devices = list(set(hass_devices).difference(set(dev_list)))

        context['hass_dev_list'] = hass_devices
        context['aa_dev_list'] = dev_list


    def get_step3(self, context):
        context['activity_list'] = Activity.objects.all()


    def get_step4(self, context):
        srv = get_server()
        hass_users = HARest().get_user_names()
        hass_users = list(set(hass_users).difference(set(Person.get_all_ha_names())))

        context['hass_user_list'] = hass_users
        context['aa_user_list'] = Person.objects.all()


    def post_step0(self, request):
        """ reads api key from environment 
            gets outside url 
            gets path to database
            and pings the activity assistant component
        """
        # Read rest SUPERVISOR_TOKEN from environment
        srv = get_server()
        srv.refresh_hass_token()


        # Get homeassistants outer ip address by selecting the first defined
        # interface
        try:
            srv.server_address = HASup().get_interface_ip(0)
        except:
            pass
        
        srv.time_zone = HARest().get_time_zone()

        srv.save()

        # only advance if the component was installed at hass site
        #if srv.hass_comp_installed:
        self._increment_one_step()


    def post_step1(self, request):
        """ Select poll interval
        """
        p_int = str(request.POST.get("poll_interval", ""))
        assert p_int in settings.POLL_INTERVAL_LST

        # Update server
        srv = get_server()
        srv.poll_interval = p_int
        srv.save()

        self._increment_one_step()


    def post_step2(self, request):
        """ Select devices to track
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
        assert from_step in SETUP_STEPS

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


    def get(self, request):
        srv = Server.objects.all()[0]
        if srv.setup == "completed":
            return redirect('/dashboard/')
        else:
            # debug
            logger.error('get')
            return render(request, 'setup.html', self.create_context())