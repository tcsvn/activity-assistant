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
from django.http import HttpResponseRedirect
import sys
import time
sys.path.append('..')

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
