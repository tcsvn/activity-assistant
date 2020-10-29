from backend.models import *
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
import datetime
import requests
import json
import os
from frontend.forms import ModelForm
import sys
from homeassistant_api.websocket import HassWs
import homeassistant_api.rest as hass_api

DATASET_NAME_HASS="homeassistant"
HASS_DB_NAME = 'home-assistant_v2.db'


class CreatePersonView(TemplateView):

    def create_context(self):
        person_list = Person.objects.all()
        context = {'person_list' : person_list }
        return context

    # list all persons and render them into the frontend
    def get(self, request):
        context = self.create_context()
        return render(request, 'create_person.html', context)

    def chooseRandActivityID(self):
        activities = Activity.objects.all()
        return activities[0].id

    def chooseRandLocationID(self):
        activities = Location.objects.all()
        return activities[0].id

    def create_person(self, request):
        name = request.POST.get("name","")
        per = Person(
            name=name
        )
        per.save()
        # todo check why this has to be done in Viewset for over API creation
        # todo and here if it is created over the web interface
        person_path = settings.HASSBRAIN_ACT_FILE_FOLDER + "/" + str(per.name)
        self._create_activity_folder_if_not_exists(person_path)
        self._create_activity_file_if_not_exists(person_path)

        # create a corresponding person in home assistant
        uid = self.person_name2id(name)
        self.create_hass_person(name, uid)


    def _create_activity_file_if_not_exists(self, folder_path):
        # create file if it not exists
        file_path = folder_path + "/" + settings.ACTIVITY_FILE_NAME
        from pathlib import Path
        act_file = Path(file_path)
        if not act_file.is_file():
            open(file_path, 'a').close()

    def _create_activity_folder_if_not_exists(self, folder_path):
        # if the folder for the person to log the activities to does not exits, create one
        import os
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)





    def create_hass_person(self, name, user_id):
        import asyncio
        hass_address = Server.objects.all()[0].hass_address
        token = Server.objects.all()[0].hass_api_token
        ws = HassWs(hass_address,  token)

        loop = asyncio.new_event_loop()
        try:
            task_obj = loop.create_task(
                self._create_hass_person_task(ws, name, user_id)
            )
            loop.run_until_complete(task_obj)
        finally:
            loop.close()

    async def _create_hass_person_task(self, ws, name, uid):
        await ws.connect()
        test = await ws.create_person(name, uid)
        return test

    def delete_person(self, request):
        pk = request.POST.get("pk", "")

        # delete corresponding person in home assistant
        uid = pk
        person = Person.objects.get(id=pk)
        person.delete()
        self.delete_hass_person(uid)

    def delete_hass_person(self, uid):
        import asyncio
        hass_address = Server.objects.all()[0].hass_address
        token = Server.objects.all()[0].hass_api_token
        ws = HassWs(hass_address,  token)

        loop = asyncio.new_event_loop()
        try:
            task_obj = loop.create_task(
                self._delete_hass_person_task(ws, uid)
            )
            loop.run_until_complete(task_obj)
        finally:
            loop.close()

    async def _delete_hass_person_task(self, ws:  HassWs, uid):
        await ws.connect()
        test = await ws.delete_person(uid)
        return test

    def person_name2id(self, name):
       for person in Person.objects.all():
           if person.name == name:
               return person.id

    def post(self, request):
        intent = request.POST.get("intent","")
        #create object not through serialzier
        if (intent == "delete"):
            self.delete_person(request)

        # create Object through serializer
        elif (intent == "create"):
            self.create_person(request)

        context = self.create_context()
        return render(request, 'create_person.html', context)

from django.http import HttpResponseRedirect
import time
class BasicConfig(TemplateView):
    def get_context(self):
        server_config = Server.objects.all()[0]
        person_list = Person.objects.all()
        access_token_available = self._is_access_token()
        return {'server_address': server_config.server_address,
                'hass_address': server_config.hass_address,
                'access_token_available': access_token_available,
                'person_list' : person_list,
                }
    def _is_access_token(self):
        srv = Server.objects.all()[0]
        return not srv.hass_api_token is None

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, 'basic_config.html', context)

    def set_server_addr(self, request):
        server = Server.objects.all()[0]
        srv_address = request.POST.get("server_address", "")
        server.server_address = srv_address
        server.save()


    def reset_server_addr(self):
        server = Server.objects.all()[0]
        server.server_address = None
        server.save()

    def set_hass_addr(self, request):
        server = Server.objects.all()[0]
        hass_address = request.POST.get("hass_address", "")
        server.hass_address = hass_address
        server.save()


    def set_access_token(self, request):
        server = Server.objects.all()[0]
        api_token = request.POST.get("hass_api_token","")
        server.hass_api_token = api_token
        server.save()
        # todo check for home assistant connection to ensure the api key and the address is correct


    def reset_hass_addr(self):
        server = Server.objects.all()[0]
        server.hass_address = None
        server.save()

    def reset_access_token(self):
        # TODO revoke key in homeassistant
        server = Server.objects.all()[0]
        server.hass_api_token = None
        server.save()

    def post(self, request):
        intent = request.POST.get("intent", "")
        
        if intent == "set_srv_addr":
            self.set_server_addr(request)

        elif intent == "reset_srv_addr":
            self.reset_server_addr()

        elif intent == "set_access_token":
            self.set_access_token(request)

        elif intent == "set_hass_addr":
            self.set_hass_addr(request)

        elif intent == "reset_hass_addr":
            self.reset_hass_addr()

        elif intent == "reset_hass_token":
            self.reset_access_token()

        context = self.get_context()
        return render(request, 'basic_config.html', context)




class ActivityView(TemplateView):
    # list all persons and render them into the frontend

    def get_context(self):
        activity_list = Activity.objects.all()
        person_list = Person.objects.all()
        return { 'activity_list' : activity_list,
                 'person_list' : person_list}

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, 'activities.html', context)

    def create_activity(self, name):
        activity = Activity()
        activity.name = name
        activity.save()

    def get_activity_by_id(self, pk):
        activity_list = Activity.objects.all()
        for act in activity_list:
            if act.id == int(pk):
                return act

    def delete_activity(self, pk):
        activity = self.get_activity_by_id(pk)
        activity.delete()

    def post(self, request):
        intent = request.POST.get("intent","")
        if (intent == "delete"):
            pk = request.POST.get("pk", "")
            self.delete_activity(pk)

        elif (intent == "create"):
            name = request.POST.get("name","")
            self.create_activity(name)

        context = self.get_context()
        return render(request, 'activities.html', context)

import sys
import time
sys.path.append('..')
class AssignSensor(TemplateView):
    # list all persons and render them into the frontend

    def get_context(self):
        person_list = Person.objects.all()
        location_list = Location.objects.all()
        device_list = Device.objects.all()
        dev_comp_list = DeviceComponent.objects.all()
        return { 'location_list': location_list,
                'device_list' : device_list,
                 'person_list' : person_list,
                 'dev_comp_list' : dev_comp_list}

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, 'assign_sensors.html', context)

    def getLocationByName(self, name):
        location_list = Location.objects.all()
        for location in location_list:
            if location.name == name:
                return location

    def _get_device_by_name(self, name):
        dev_list = Device.objects.all()
        for dev in dev_list:
            if dev.name == name:
                return dev

    def assign_device(self, device_name, location_name):
        location = self.getLocationByName(location_name)
        device = self._get_device_by_name(device_name)
        device.location = location
        device.save()


    def unassign_device(self, device_name):
        device = self._get_device_by_name(device_name)
        device.location = None
        device.save()
        #self.put_device(name, 'reset')

    def post(self, request):
        intent = request.POST.get("intent","")

        if (intent == "assign_device"):
            device_name = request.POST.get("device_name","")
            location_name = request.POST.get("location_name","")
            self.assign_device(device_name, location_name)

        elif (intent == "unassign_device"):
            device_name = request.POST.get("device_name","")
            self.unassign_device(device_name)

        elif (intent == "synchronize"):
            self.synchronize()
        context = self.get_context()
        return render(request, 'assign_sensors.html', context)

    def synchronize(self):
        url = Server.objects.all()[0].hass_address
        token = Server.objects.all()[0].hass_api_token
        device_list = self._dev_comp2_compnameslst()
        print(device_list)
        res_dict = hass_api.get_filtered_devices(
            url,
            token,
            device_list
        )
        print('*'*100)
        print('url: ', url)
        print('token: ', token)
        print(res_dict)
        print('*'*100)
        self.create_only_new(res_dict)

    def _dev_comp2_compnameslst(self):
        dev_comps = DeviceComponent.objects.all()
        res_lst = []
        for dev_comp in dev_comps:
            res_lst.append(dev_comp.name)
        return res_lst


    def create_only_new(self, new_devices):
        device_list = Device.objects.all()
        to_delete_sensors = []
        for old in device_list:
            old_present_in_new = False
            for new in new_devices:
                if new['name'] == old.name:
                    new_devices.remove(new)
                    old_present_in_new = True
                    break
                # if an established device isn't in present on homeassistant
                # then delete the old one
            if not old_present_in_new:
                to_delete_sensors.append(old)

        # apply changes to api
        self.delete_obsolete_devices(to_delete_sensors)
        self.create_new_devices(new_devices)


    def delete_obsolete_devices(self, device_list):
        for device in device_list:
            device.delete()

    def _get_component_by_name(self, name):
        for comp in DeviceComponent.objects.all():
            if comp.name == name:
                return comp


    def create_new_devices(self, dev_list):
        for item in dev_list:
            component = self._get_component_by_name(item['component'])
            new_dev = Device(
                name=item['name'],
                state='off',
                location=None,
                component=component
            )
            new_dev.save()

class AssignActivities(TemplateView):
    # list all persons and render them into the frontend

    def get_context(self):
        person_list = Person.objects.all()
        location_list = Location.objects.all()
        activity_list = Activity.objects.all()
        return { 'location_list': location_list,
                 'person_list' : person_list,
                 'activity_list' : activity_list
                 }

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, 'assign_activity_location.html', context)

    def getLocationByName(self, name):
        location_list = Location.objects.all()
        for location in location_list:
            if location.name == name:
                return location

    def _get_activity_by_name(self, name):
        act_list = Activity.objects.all()
        for act in act_list:
            if act.name == name:
                return act

    def assign_activity(self, activity_name, location_name):
        location = self.getLocationByName(location_name)
        activity = self._get_activity_by_name(activity_name)
        activity.locations.add(location)
        activity.save()


    def unassign_device(self, activity_name, location_name):
        location = self.getLocationByName(location_name)
        activity = self._get_activity_by_name(activity_name)
        activity.locations.remove(location)
        activity.save()


    def post(self, request):
        intent = request.POST.get("intent","")

        if (intent == "assign_activity"):
            activity_name = request.POST.get("activity_name","")
            location_name = request.POST.get("location_name","")
            self.assign_activity(activity_name, location_name)

        elif (intent == "unassign_activity"):
            print('*'*100)
            activity_name = request.POST.get("activity_name","")
            location_name = request.POST.get("location_name","")
            print(location_name)
            print(activity_name)
            print('*'*100)
            self.unassign_device(activity_name, location_name)

        context = self.get_context()
        return render(request, 'assign_activity_location.html', context)


class EditMapView(TemplateView):

    def get_context(self):
        location_list = Location.objects.all()
        person_list = Person.objects.all()
        edge_list = Edge.objects.all()
        context = {
                "edge_list" : edge_list,
                "person_list": person_list,
                "location_list" : location_list 
                }
        return context

    def create_new_graph(self, nodes, edges):
        self.delete_locations()
        self.create_locations(nodes)
        # edges are deleted with nodes therefore further action is unessecary
        webID_to_restID = self.get_node_test(nodes)
        self.create_edges(edges, webID_to_restID)

    # create a mapping from the ids of the javascript nodes to ids of rest api nodes
    def get_node_test(self, web_nodes):
        loc_list = Location.objects.all()
        node_dict = {}
        for node in loc_list:
            for web_node in web_nodes:
                if node.name == web_node['title']:
                    node_dict[web_node['id']] = node.pk
        return node_dict

    def create_edges(self, edges, webID_to_restID):
        for edge in edges:
            src = Location.objects.get(id=webID_to_restID[edge['source']])
            snk = Location.objects.get(id=webID_to_restID[edge['target']])
            new_edge = Edge(
                source=src,
                sink=snk
            )
            new_edge.save()

    def create_locations(self, nodes):
        for node in nodes:
            loc = Location(
                node_id=node['id'],
                name=node['title'],
                x=node['x'],
                y=node['y']
            )
            loc.save()

    def delete_locations(self):
        location_list = Location.objects.all()       
        for location in location_list:
            location.delete()

    def post(self, request, **kwargs):
        graph = json.loads(request.POST.get("content",""))
        self.create_new_graph(graph['nodes'], graph['edges'])

        context = self.get_context() 
        return render(request, 'map.html', context)

    # list all persons and render them into the frontend
    def get(self, request):
        context = self.get_context()
        return render(request, 'map.html', context)
