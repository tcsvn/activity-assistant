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