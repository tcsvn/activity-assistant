from django.views.generic import TemplateView
from backend.models import *
from backend.models import Area, Device
from frontend.util import get_server
from django.shortcuts import render, redirect
from hass_api.rest import HARest

class AssignDeviceView(TemplateView):
    # list all persons and render them into the frontend
    HTML = 'config/assign_devices.html'

    def get_context(self):
        srv = get_server()
        person_list = Person.objects.all()
        area_list = Area.objects.all()
        device_list = Device.objects.all()
        
        return dict(
            area_list=area_list,
            device_list=device_list,
            person_list=person_list,
            experiment_active=srv.is_experiment_running(),
        )

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, self.HTML, context)

    def assign_device(self, request):
        device_name = request.POST.get("device_name","").strip()
        area_name = request.POST.get("area_name","").strip()
        area = Area.by_name(area_name)
        device = Device.by_name(device_name)
        device.area = area
        device.save()


    def unassign_device(self, request):
        device_name = request.POST.get("device_name","").strip()
        device = Device.by_name(device_name)
        device.area = None
        device.save()
        #self.put_device(name, 'reset')


    def add_area(self, request):
        area_name = request.POST.get("area_name","")
        assert area_name 
        area = Area(name=area_name)
        area.save()

    def delete_area(self, request):
        area_name = request.POST.get("area_name","")
        area = Area.by_name(area_name)
        area.delete()

    def fetch_areas_from_ha(self):
        devices = Device.get_all_names()
        har = HARest()
        mapping = har.get_dev_area_mapping(devices, only_matches=True)
        areas = set(mapping.values())

        for area in areas:
            Area(name=area).save()

        for dev_name in mapping.keys():
            dev = Device.by_name(dev_name)
            dev.area = Area.by_name(mapping[dev_name])
            dev.save()


    def post(self, request):
        intent = request.POST.get("intent","")

        if (intent == "assign_device"):
            self.assign_device(request)
        elif (intent == "unassign_device"):
            self.unassign_device(request)
        elif intent == "fetch_from_ha":
            self.fetch_areas_from_ha()
        elif intent == "delete_area":
            self.delete_area(request)
        elif intent == "add_area":
            self.add_area(request)

        context = self.get_context()
        return render(request, self.HTML, context)