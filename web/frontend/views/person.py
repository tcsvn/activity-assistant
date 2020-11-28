from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server

# css frontend
class PersonView(TemplateView):
    # list all persons and render them into the frontend
    def create_context(self, request):
        person_list = Person.objects.all()
        # get current person id from url
        pk = self._getPersonPk(request)
        person = Person.objects.get(pk=int(pk))
        pred_acts = person.predicted_activities.all()
        activity_list = Activity.objects.all()
        syn_act_list = SyntheticActivity.objects.filter(person=person)
        person_list = Person.objects.all()
        try:
            smartphone = person.smartphone
        except:
            smartphone = None
        qr_code_data = self.generate_qr_code_data(person)
        context = {
                'person' : person,
                'smartphone' : smartphone, 
                'person_list' : person_list,
                'activity_list' : activity_list,
                'synthetic_activity_list':  syn_act_list,
                'qr_code_data' : qr_code_data
                }
        if pred_acts is not None:
            context['predicted_activities'] = pred_acts
        return context

    def _getPersonPk(self, request):
        pk = request.POST.get("pk", "")
        if pk == "":
            if request.get_full_path().split("/")[-1] == "":
                return request.get_full_path().split("/")[-2]
            else:
                return request.get_full_path().split("/")[-1]
        else:
            return pk



    def get(self, request):
        context = self.create_context(request)
        return render(request, 'person.html', context)

    def _get_activity_by_name(self, name):
        act_list = Activity.objects.all()
        for act in act_list:
            if act.name == name:
                return act

    def create_syn_act(self, request):
        activity_name = request.POST.get("activity_name", "")
        day_of_week = request.POST.get("day_of_week", "")
        start = request.POST.get("start", "")
        end = request.POST.get("end", "")

        start_time = datetime.time.fromisoformat(start)
        end_time = datetime.time.fromisoformat(end)

        pk = request.get_full_path().split("/")[-1]
        person = Person.objects.get(pk=int(pk))
        activity = self._get_activity_by_name(activity_name)
        syn_act = SyntheticActivity(
            person=person,
            start=start_time,
            synthetic_activity=activity,
            end=end_time,
            day_of_week=day_of_week
        )
        syn_act.save()

    def delete_syn_act(self, request):
        pk = request.POST.get("pk", "")
        syn_act = SyntheticActivity.objects.get(pk=int(pk))
        syn_act.delete()

    def update_syn_act(self, request):
        pk = request.POST.get("pk", "")
        day_of_week = request.POST.get("day_of_week", "")
        start = request.POST.get("start", "")
        end = request.POST.get("end", "")

        syn_act = SyntheticActivity.objects.get(pk=int(pk))
        start_time = datetime.time.fromisoformat(start)
        end_time = datetime.time.fromisoformat(end)
        syn_act.start = start_time
        syn_act.end = end_time
        syn_act.day_of_week = day_of_week
        syn_act.save()

    def _get_person_from_request(self, request):
        pk = request.POST.get("pk", "")
        return Person.objects.filter(pk=int(pk))[0]

    def retrieve_retrieve_syn_acts(self, request):
        from django.http import JsonResponse
        from .algorithm import AlgorithmView
        person = self._get_person_from_request(request)
        act_data = AlgorithmView.get_activity_data(person)
        loc_data = AlgorithmView.get_location_data()
        resp = {'activity_data': act_data, 'loc_data': loc_data}
        return JsonResponse(resp)

    def post(self, request):
        intent = request.POST.get("intent","")
        #create object not through serialzier
        if (intent == "create_syn_act"):
            self.create_syn_act(request)

        elif (intent == "delete_syn_act"):
            self.delete_syn_act(request)

        elif (intent == "update_syn_act"):
            self.update_syn_act(request)

        elif (intent == "export_data"):
            return self.retrieve_retrieve_syn_acts(request)

        context = self.create_context(request)
        return render(request, 'person.html', context)

    def generate_qr_code_data(self, person):
        url = get_server().server_address
        data = "{"
        data += "\"person\" : \"%s\" , "%(person.name)
        data += "\"username\" : \"%s\" , "%('admin')
        data += "\"password\" : \"%s\" , "%('asdf')
        data += "\"url_person\" : \"%s\" ,"%('persons/' + str(person.id) + '/')
        data += "\"url_api\" : \"%s\""%(url + '/api/v1/')
        data += "}"
        return data


