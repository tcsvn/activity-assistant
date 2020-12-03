from backend.models import *
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from frontend.util import get_server, get_device_names
from zipfile import ZipFile 
import pathlib
import logging
from django.http import FileResponse
logger = logging.getLogger(__name__)

# css frontend
class DatasetView(TemplateView):
    # list all persons and render them into the frontend
    def create_context(self, request):
        context = {}
        context['person_list'] = Person.objects.all()
        context['dataset_list'] = Dataset.objects.all()
        srv = get_server()
        if srv.dataset is not None:
            context['dataset'] = srv.dataset
            context['experiment_running'] = True
            context['polling'] = srv.is_polling
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
        except FileNotFoundException:
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
        generate_device_analysis(ds)


    def get(self, request):
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

    def post(self, request):
        intent = request.POST.get("intent","")
        assert intent in ['delete_dataset', 'export_dataset', 'generate_analysis']
        if intent == 'delete_dataset':
            self.delete_dataset(request)
        elif intent == 'export_dataset':
            return self.export_dataset(request)
        elif intent == 'generate_analysis':
            self.generate_analysis(request)
        context = self.create_context(request)
        return render(request, 'dataset.html', context)

def gen_plots_persons(dataset, data, root_path):
    from pyadlml.dataset.plot.activities import hist_counts, boxplot_duration, \
        hist_cum_duration, heatmap_transitions, ridge_line

    for ps in dataset.person_statistics.all():
        sub_path = dataset.name + '/plots/' + ps.name + '/'
        path = settings.MEDIA_ROOT + sub_path

        # generate plots
        hist_counts_filename = 'hist_counts.png'
        path_to_hist_counts = path + hist_counts_filename
        hist_counts(data.df_activities, file_path=path_to_hist_counts)
        ps.plot_hist_counts = sub_path + hist_counts_filename

        boxplot_duration_filename = 'boxplot_duration.png'
        path_to_boxplot_duration = path + boxplot_duration_filename
        boxplot_duration(data.df_activities, file_path=path_to_boxplot_duration)
        ps.plot_boxplot_duration = sub_path + boxplot_duration_filename

        hist_cum_duration_filename = 'hist_cum_duration.png'
        path_to_hist_cum_duration = path + hist_cum_duration_filename
        hist_cum_duration(data.df_activities, file_path=path_to_hist_cum_duration)
        ps.plot_hist_cum_duration = sub_path + hist_cum_duration_filename

        heatmap_transitions_filename = 'heatmap_transitions.png'
        path_to_heatmap_transitions = path + heatmap_transitions_filename
        heatmap_transitions(data.df_activities, file_path=path_to_heatmap_transitions)
        ps.plot_heatmap_transitions = sub_path + heatmap_transitions_filename

        ridge_line_filename = 'ridge_line.png'
        path_to_ridge_line = path + ridge_line_filename
        ridge_line(data.df_activities, file_path=path_to_ridge_line)
        ps.plot_ridge_line = sub_path + ridge_line_filename
        ps.save()

def generate_device_analysis(dataset):
    """
    """
    import pyadlml.dataset._datasets.activity_assistant as act_assist
    data = act_assist.load(dataset.path_to_folder, 'admin')

    root_path = settings.MEDIA_ROOT + dataset.name + '/'

    #gen_plots_persons(dataset, data, root_path)

    from pyadlml.dataset.plot.devices import hist_trigger_time_diff, boxplot_on_duration, \
        heatmap_trigger_one_day, heatmap_trigger_time, heatmap_cross_correlation, \
        hist_on_off, hist_counts

    logger.error(str(data.df_devices.head()))
    sub_path = dataset.name + '/plots/'
    path = settings.MEDIA_ROOT + sub_path
    logger.error('path: ' + path)
    logger.error('subpath: ' + sub_path)

    hist_trigger_time_diff_filename = 'hist_trigger_time_diff.png'
    path_to_hist_trigger_time_diff = path + hist_trigger_time_diff_filename
    hist_trigger_time_diff(data.df_devices, file_path=path_to_hist_trigger_time_diff)
    dataset.plot_hist_trigger_time_diff = sub_path + hist_trigger_time_diff_filename

    heatmap_trigger_time_filename = 'heatmap_trigger_time.png'
    path_to_heatmap_trigger_time = path + heatmap_trigger_time_filename
    heatmap_trigger_time(data.df_devices, file_path=path_to_heatmap_trigger_time)
    dataset.plot_heatmap_trigger_time = sub_path + heatmap_trigger_time_filename

    heatmap_trigger_one_day_filename = 'heatmap_trigger_one_day.png'
    path_to_heatmap_trigger_one_day = path + heatmap_trigger_one_day_filename
    heatmap_trigger_one_day(data.df_devices, file_path=path_to_heatmap_trigger_one_day)
    dataset.plot_heatmap_trigger_one_day = sub_path + heatmap_trigger_one_day_filename

    hist_counts_filename = 'hist_counts.png'
    path_to_hist_counts = path + hist_counts_filename
    hist_counts(data.df_devices, file_path=path_to_hist_counts)
    dataset.plot_hist_counts = sub_path + hist_counts_filename

    # TODO add conversion to pyadlml
    #assign_plot_obj('boxplot_on_duration.png', boxplot_on_duration, dataset.plot_boxplot_on_duration,
    #                    path, sub_path, data.df_devices)
    #assign_plot_obj('hist_on_off.png', hist_on_off, dataset.plot_hist_on_off,
    #                    path, sub_path, data.df_devices)

    dataset.save()

def assign_plot_obj(filename, func, attr, total_path, rel_path, df_acts):
    path_to_file = total_path + filename
    func(df_acts, file_path=path_to_file)
    attr = rel_path + filename
    logger.error('hc path: ' + path_to_file)
    logger.error('hc subpath: ' + rel_path + filename)


def savefig(fig, file_path):
    """ saves figure to folder and if folder doesn't exist create one
    """
    import matplotlib.pyplot as plt
    import os
    folder_path = file_path.rsplit('/', 1)[0]
    if not os.path.isdir(folder_path):
        os.makedirs(folder_path)
    plt.savefig(file_path)



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