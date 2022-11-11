from django.views.generic import TemplateView
from backend.models.models import Person, Area, Activity
from django.shortcuts import render, redirect


class AssignActivityView(TemplateView):
    # list all persons and render them into the frontend

    def get_context(self):
        person_list = Person.objects.all()
        location_list = Area.objects.all()
        activity_list = Activity.objects.all()
        return { 'location_list': location_list,
                 'person_list' : person_list,
                 'activity_list' : activity_list
                 }

    def get(self, request, *args, **kwargs):
        context = self.get_context()
        return render(request, 'config/assign_activity.html', context)

    def getLocationByName(self, name):
        location_list = Area.objects.all()
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
        #activity.locations.add(location)

        activity.save()


    def unassign_device(self, activity_name, location_name):
        location = self.getLocationByName(location_name)
        activity = self._get_activity_by_name(activity_name)
        #activity.area.remove(location)
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

