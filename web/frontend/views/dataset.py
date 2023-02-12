from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server
import pathlib
import shutil
import logging
from frontend.util import collect_data_from_hass, get_line_numbers_file, get_folder_size
logger = logging.getLogger(__name__)



class DatasetView(TemplateView):

    def create_context(self, request):
        context = {}
        context['person_list'] = Person.objects.all()
        context['dataset_list'] = Dataset.objects.all()
        context['activity_list'] = Activity.objects.all()

        srv = get_server()
        ds = srv.dataset
        if ds is not None:
            ds.update_statistics()
            context['dataset'] = ds
            context['experiment_running'] = True
            context['polling'] = srv.is_polling
        else:
            context['experiment_running'] = False
            dev_lst = Device.get_all_names()
            context['device_lst'] = dev_lst
            context['num_devs'] = len(dev_lst)
        return context

    def delete_dataset(self, request):
        name = request.POST.get("dataset_name","")
        Dataset.objects.get(name=name).delete()

    def export_dataset(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)
        srv = get_server()

        if srv.is_experiment_running() and srv.dataset.name == name:
            # If dataset to export is the active experiment gather all data
            # first
            collect_data_from_hass()
            for person in Person.objects.all():
                if hasattr(person, 'hatracker'):
                    person.hatracker.transform_activity_df()
            ds.collect_activity_files()

        return ds.get_fileResponse()


    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

    def post(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['delete_dataset', 'export_dataset']

        if intent == 'delete_dataset':
            self.delete_dataset(request)
        elif intent == 'export_dataset':
            return self.export_dataset(request)


        context = self.create_context(request)
        return render(request, 'dataset.html', context)

def collect_person_statistics(ps):
    """ gets the number of activities, number of recorded activities and activity file datasize
    """
    activity_fp = ps.get_activity_fp()
    num_activities = get_line_numbers_file(
        ps.dataset.path_to_folder + settings.ACTIVITY_MAPPING_FILE_NAME) -1
    num_recorded_activities = get_line_numbers_file(activity_fp) -1
    data_size = get_folder_size(activity_fp)
    return num_activities, num_recorded_activities, data_size

#def collect_dataset_statistics(dataset):
#    for ps in dataset.person_statistics.all():
#        num_acts, num_rec_acts, act_data_size = collect_person_statistics(ps)
#        ps.num_activities = num_acts
#        ps.num_recorded_activities = num_rec_acts
#        ps.save()
#        data_size += act_data_size
#
#    dataset.data_size = data_size
#    dataset.save()


#def savefig(fig, file_path):
#    """ saves figure to folder and if folder doesn't exist create one
#    """
#    import matplotlib.pyplot as plt
#    import os
#    folder_path = file_path.rsplit('/', 1)[0]
#    if not os.path.isdir(folder_path):
#        os.makedirs(folder_path)
#    plt.savefig(file_path)


