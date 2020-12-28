from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
from zipfile import ZipFile 
import pathlib
import shutil
import logging
from django.http import FileResponse
from frontend.experiment import copy_actfiles2dataset
from frontend.util import collect_data_from_hass, get_line_numbers_file, get_folder_size
logger = logging.getLogger(__name__)

def get_datasets_personal_statistics():
    """ creates a dictionary for every dataset with statistics like
        number of persons, total number of recorded activities
        and number of activities. This is used for display in templates
    """
    srv = get_server()
    hackdct = []
    for ds in Dataset.objects.all():
        if srv.dataset is not None and srv.dataset.name == ds.name:
            continue
        tmp = {}
        tmp['ds_name'] = ds.name
        tmp['num_persons'] = len(ds.person_statistics.all())
        for ps in ds.person_statistics.all():
            tmp['num_activities']  = ps.num_activities
        try:
            num_rec_acts = 0
            for ps in ds.person_statistics.all():
                tmp['num_activities']  = ps.num_activities
                num_rec_acts += ps.num_recorded_activities
            tmp['num_recorded_activities'] = num_rec_acts
        except TypeError:
            # this is catches the case when somebody has not evaluated the statistic
            # and therefore this quantitiy shouldn't be set
            tmp['num_recorded_activities'] = None
        hackdct.append(tmp)
    return hackdct

# css frontend
class DatasetView(TemplateView):
    # list all persons and render them into the frontend
    def create_context(self, request):
        context = {}
        context['person_list'] = Person.objects.all()
        context['dataset_list'] = Dataset.objects.all()
        context['activity_list'] = Activity.objects.all()

        srv = get_server()
        context['service_plot_gen'] = (srv.plot_gen_service_pid is not None)
        try:
            context['datasets_perstats'] = get_datasets_personal_statistics()
        except:
            pass

        if srv.dataset is not None:
            context['dataset'] = srv.dataset
            context['experiment_running'] = True
            context['polling'] = srv.is_polling
            context['num_persons'] = len(context['person_list'])
            context['num_activities'] = len(context['activity_list'])
        else:
            context['experiment_running'] = False
            dev_lst = get_device_names()
            context['device_lst'] = dev_lst
            context['num_devs'] = len(dev_lst)
        return context

    def delete_dataset(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)
        path = ds.path_to_folder
        import shutil
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
        ds.delete()

    def export_dataset(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)

        # create zip at location
        path_to_zip = settings.MEDIA_ROOT + ds.name + ".zip"
        create_zip(ds.path_to_folder, path_to_zip)

        # create response
        zip_file = open(path_to_zip, 'rb')
        response = FileResponse(zip_file)

        # cleanup zip file
        rem_file = pathlib.Path(path_to_zip)
        rem_file.unlink()
        return response

    def generate_analysis(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)

        collect_dataset_statistics(ds)
        set_placeholder_images(ds)
        start_plot_gen_service(ds)

    def generate_analysis_for_exp(self, request):
        name = request.POST.get("dataset_name","")
        ds = Dataset.objects.get(name=name)

        copy_actfiles2dataset(ds)
        collect_data_from_hass()
        collect_dataset_statistics(ds)

        set_placeholder_images(ds)
        start_plot_gen_service(ds)


    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

    def post(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['delete_dataset', 'export_dataset', 'generate_analysis', \
            'gen_analysis_for_experiment']
        if intent == 'delete_dataset':
            self.delete_dataset(request)
        elif intent == 'export_dataset':
            return self.export_dataset(request)
        elif intent == 'generate_analysis':
            self.generate_analysis(request)
        elif intent == 'gen_analysis_for_experiment':
            self.generate_analysis_for_exp(request)

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

def collect_device_statistics(dataset):
    """ gets the number of devices, number of recorded events and device file datasize
    """
    num_devices = get_line_numbers_file(
        dataset.path_to_folder + settings.DATA_MAPPING_FILE_NAME) -1
    num_recorded_events = get_line_numbers_file(
        dataset.path_to_folder + settings.DATA_FILE_NAME) -1
    data_size = get_folder_size(
        dataset.path_to_folder + settings.DATA_FILE_NAME
        )
    return num_devices, num_recorded_events, data_size

def collect_dataset_statistics(dataset):
    num_devices, num_rec_events, data_size = collect_device_statistics(dataset)
    dataset.num_devices = num_devices
    dataset.num_recorded_events = num_rec_events

    for ps in dataset.person_statistics.all():
        num_acts, num_rec_acts, act_data_size = collect_person_statistics(ps) 
        ps.num_activities = num_acts
        ps.num_recorded_activities = num_rec_acts
        ps.save()
        data_size += act_data_size

    dataset.data_size = data_size
    dataset.save()


def savefig(fig, file_path):
    """ saves figure to folder and if folder doesn't exist create one
    """
    import matplotlib.pyplot as plt
    import os
    folder_path = file_path.rsplit('/', 1)[0]
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    plt.savefig(file_path)


def set_placeholder_images(dataset):
    """ sets all plots to a grey placeholder image
    """
    filename = 'plot_placeholder.png'
    placeholder_image_path = settings.STATIC_ROOT + 'images/' + filename
    placeholder_media_path = settings.MEDIA_ROOT + '/' +  filename

    # copy from static to media  
    if not Path(placeholder_media_path).is_file():
        from_file = pathlib.Path(placeholder_image_path)
        to_file = pathlib.Path(placeholder_media_path)
        shutil.copy(from_file, to_file) 

    logger.error(placeholder_image_path)
    for ps in dataset.person_statistics.all():
        ps.plot_hist_counts = filename
        ps.plot_boxplot_duration = filename
        ps.plot_hist_cum_duration = filename
        ps.plot_heatmap_transitions = filename
        ps.plot_ridge_line = filename
        ps.save()
    
    dataset.plot_hist_trigger_time_diff = filename
    dataset.plot_heatmap_trigger_time = filename
    dataset.plot_heatmap_trigger_one_day = filename
    dataset.plot_hist_counts = filename
    dataset.plot_hist_on_off = filename
    dataset.plot_boxplot_on_duration = filename
    dataset.plot_heatmap_cross_correlation = filename
    dataset.save()

def create_zip(folder_to_zip, dest_path):
    """ zips a folder with all files at the base and saves it at given location
    Parameters
    ----------
    folder_to_zip : String
        the path to the folder that is going to be zipped
    dest_path : String
        the path where the resulting zip file is going to be stored
    """
        # collect recursively all files in subfolder
    file_paths = []
    for root, directories, files in os.walk(folder_to_zip):
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # writing files to a zipfile 
    from os.path import basename
    with ZipFile(dest_path,'w') as zip: 
        # writing each file one by one 
        for f in file_paths: 
            zip.write(f, arcname=basename(f)) 


def start_plot_gen_service(dataset):
    """ starts a process that generates plots for a given dataset
    Parameters
    ----------
    dataset : model.Dataset
    """
    import subprocess
    srv = get_server()
    command = ["python3", settings.PLOT_GEN_SERVICE_PATH]
    command += ['--dataset-id', str(dataset.id)]
    if settings.DEBUG:
        command += ['--debug']

    proc = subprocess.Popen(command, close_fds=True)
    srv.plot_gen_service_pid = proc.pid 
    srv.save()

def kill_plot_get_service(dataset):
    import os
    import signal
    srv = get_server()
    pid = srv.plot_gen_service_pid
    if pid is not None:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            logger.error('process plot gen allready deleted')
        srv.plot_gen_service_pid = None
        srv.save()