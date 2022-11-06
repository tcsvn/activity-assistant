from backend.models import *
from hass_api.rest import HARest
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server

import logging
logger = logging.getLogger(__name__)

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
        try:
            smartphone = person.smartphone
        except:
            smartphone = None
        try:
            ha_tracker = person.hatracker
        except:
            ha_tracker = None

        try:
            ha_tracker.update_attributes()
        except Exception:
            pass

        if ha_tracker is not None:
            if not ha_tracker.inputxs_exist_at_ha():
                ha_tracker.delete()
                ha_tracker = None
                person.hatracker = None
                person.save()


        qr_code_data = self.generate_qr_code_data(person)
        sm_download_link = settings.ACT_ASSIST_RELEASE_LINK

        ha_input_selects = self.get_input_selects()
        ha_input_booleans = self.get_input_booleans()

        context = {
                'person' : person,
                'smartphone' : smartphone,
                'hatracker' : ha_tracker,
                'person_list' : person_list,
                'activity_list' : activity_list,
                'synthetic_activity_list':  syn_act_list,
                'qr_code_data' : qr_code_data,
                'qr_code_sm_download' : sm_download_link,
                'ha_input_select_list': ha_input_selects,
                'ha_input_boolean_list': ha_input_booleans,
                }
        if person.person_statistic is not None:
            context['ps'] = person.person_statistic
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

    def get_input_booleans(self):
        from hass_api.rest import HARest
        devices = \
            [d for d in HARest().get_device_list() if 'input_boolean' in d]
        return devices


    def get_input_selects(self):
        from hass_api.rest import HARest
        devices = \
            [d for d in HARest().get_device_list() if 'input_select' in d]
        return devices

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


    def create_input_select(self, request):
        person = self._get_person_from_request(request)
        raise NotImplementedError

    def add_input_x(self, request):
        """ Create an HA tracker for a given input_select and input_boolean
        """
        person = self._get_person_from_request(request)
        input_select = request.POST['input_select']
        input_boolean = request.POST['input_boolean']

        # Populate input_select with current activities
        act_list = list(Activity.objects.all().values_list('name', flat=True))
        HARest().populate_input_selects(input_select, act_list)

        # Update persons model for the poll stuff
        HATracker(
            person=person,
            logging=False,
            logged_activity=None,
            input_select=input_select,
            input_boolean=input_boolean
        ).save()

    def post(self, request):

        intent = request.POST.get("intent","")
        #create object not through serialzier
        if intent == "create_syn_act":
            self.create_syn_act(request)

        elif intent == "delete_syn_act":
            self.delete_syn_act(request)

        elif intent == "update_syn_act":
            self.update_syn_act(request)

        elif intent == "export_data":
            return self.retrieve_retrieve_syn_acts(request)
        elif intent ==  'create_input_select':
            self.create_input_select(request)
        elif intent == 'add_inputx':
            self.add_input_x(request)

        context = self.create_context(request)
        return render(request, 'person.html', context)

    def generate_qr_code_data(self, person) -> str:
        """ Creates string of an dictionary describing the person for the
            activity logger.
        """
        url = get_server().server_address
        data = "{"
        data += f"\"person\" : \"{person.name}\" , "
        data += f"\"username\" : \"{'admin'}\" , "
        data += f"\"password\" : \"{'asdf'}\" , "
        data += f"\"url_person\" : \"persons/{str(person.id)}/\" ,"
        data += f"\"url_api\" : \"{url}/{settings.REST_API_URL}/\""
        data += "}"
        return data