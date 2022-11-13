from django.views.generic import TemplateView
from backend.models.models import Person, Area, Activity
from django.shortcuts import render, redirect

from frontend.util import get_server


class AssignActivityView(TemplateView):
    # list all persons and render them into the frontend

    TEMPLATE_PATH = 'config/assign_activity.html'

    def get_context(self):
        srv = get_server()
        person_list = Person.objects.all()
        area_list = Area.objects.all()
        activity_list = Activity.objects.all()
        
        return { 'area_list': area_list,
                 'person_list' : person_list,
                 'activity_list' : activity_list,
                 'experiment_active': srv.is_experiment_running
                 }

    def get(self, request, *args, **kwargs):
        return render(request, self.TEMPLATE_PATH, self.get_context())

    def assign_activity(self, request):

        # Retrieve names
        activity_name = request.POST.get("activity_name","")
        area_name = request.POST.get("area_name","")

        # Get objects
        area = Area.objects.get(name=area_name)
        activity = Activity.objects.get(name=activity_name)

        # Add area to activity
        activity.areas.add(area)
        activity.save()


    def unassign_device(self, request):
        # Retrieve names
        activity_name = request.POST.get("activity_name","")
        area_name = request.POST.get("area_name","")

        # Get objects
        area = Area.objects.get(name=area_name)
        activity = Activity.objects.get(name=activity_name)

        # Remove area from activity
        activity.areas.remove(area)
        activity.save()


    def post(self, request):
        intent = request.POST.get("intent","")

        if (intent == "assign_activity"):
            self.assign_activity(request)

        elif (intent == "unassign_activity"):
            self.unassign_device(request)

        return render(request, self.TEMPLATE_PATH, self.get_context())