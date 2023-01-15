import shutil
import pathlib
import pandas as pd
from pathlib import Path
from django.db import models
from pygments.lexers import get_all_lexers
from pyadlml.constants import TIME, DEVICE, VALUE, START_TIME, END_TIME, ACTIVITY
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from pyadlml.dataset._core.activities import create_empty_activity_df
from django.core.files import File
from django.http import FileResponse
from backend.util import create_zip



class Dataset(models.Model):
    # todo mark for deletion line below
    name = models.CharField(null=True, max_length=100)
    path_to_folder = models.CharField(null=True, max_length=100)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    num_devices = models.IntegerField(null=True)
    num_recorded_events = models.IntegerField(null=True)
    num_persons = models.IntegerField(null=True)
    num_activities = models.IntegerField(null=True)
    num_recorded_activities = models.IntegerField(null=True)
    data_size = models.IntegerField(null=True)



    def collect_activity_files(self):
        """ Get the activity files from a person. Apply optional mapping 
            and overwrite the files from the dataset.
        """
        from backend.models import Person
        # Substitute activity with mapping
        act_map = self.load_activity_mapping(as_dict=True)
        for person in Person.objects.all():
            fn = person.get_activity_file_fp().name
            src = Path('/tmp').joinpath(fn)
            df = person.remap_activity_file(act_map, inplace=False)
            df.to_csv(str(src), sep=',', index=False)       

            # copy stuff activity files persons to dataset folder
            dest = Path(self.path_to_folder).joinpath(src.name)
            shutil.copyfile(src, dest) 

    def update_statistics(self):
        from frontend.util import get_line_numbers_file, get_folder_size
        dsfp = self.path_to_folder
        self.num_recorded_events = get_line_numbers_file(
                                dsfp + settings.DATA_FILE_NAME) -1
        self.data_size = get_folder_size(
                                dsfp + settings.DATA_FILE_NAME)
        self.num_activities = get_line_numbers_file(dsfp + settings.ACTIVITY_MAPPING_FILE_NAME) - 1
        self.num_devices = get_line_numbers_file(dsfp + settings.DATA_MAPPING_FILE_NAME) - 1

        total_activities = 0
        person_count = 0
        for fp in Path(dsfp).iterdir():
            if 'activities_subject_' in str(fp):
                person_count += 1
                total_activities += get_line_numbers_file(str(fp)) -1
        self.num_persons = person_count
        self.num_recorded_activities = total_activities
        self.save()

    def setup_experiment_folder(self):
        Path(self.path_to_folder).mkdir(mode=0o777, parents=True, exist_ok=False)
        self.create_data_file()
        self.create_device_mapping_file()
        self.create_activity_mapping_file()


    def create_dev2room_assignment(self):
        from backend.models import Device
        data = []
        for device in Device.objects.all():
            area = device.area.name if device.area is not None else None
            data.append([device.name, area])

        df = pd.DataFrame(data=data, columns=[DEVICE, 'area'])

        path_to_folder = self.path_to_folder
        fp = path_to_folder + settings.DEVICE_AREA_MAP_FN
        df.to_csv(fp, sep=',', index=False)       

    def create_act2room_assignment(self):
        from backend.models import Activity
        data = []
        for act in Activity.objects.all():
            for area in act.areas.all():
                data.append([act.name, area.name])

        df = pd.DataFrame(data=data, columns=[ACTIVITY, 'area'])

        path_to_folder = self.path_to_folder
        fp = path_to_folder + settings.ACTIVITY_AREA_MAP_FN
        df.to_csv(fp, sep=',', index=False)       

    def get_device_fp(self):
        return self.path_to_folder + settings.DATA_FILE_NAME

    def get_activity_fp(self, person_name):
        return self.path_to_folder + settings.ACTIVITY_FILE_NAME%(person_name)

    def get_activity_map_fp(self):
        return self.path_to_folder + settings.ACTIVITY_MAPPING_FILE_NAME

    def create_data_file(self):
        """ creates inital device file 
        Example
            time,device,val
        """
        path_to_folder = self.path_to_folder
        fp = path_to_folder + settings.DATA_FILE_NAME
        pd.DataFrame(columns=[TIME, DEVICE, VALUE])\
            .to_csv(fp, sep=',', index=False)

    def create_device_mapping_file(self):
        """ creates a device mapping file with the current devices selected
            for logging. 

        Example
            id,devices
            0,binary_sensor.ping_chris_laptop
            1,binary_sensor.ping_chris_pc
        """
        from backend.models import Device
        file_path = self.path_to_folder + settings.DATA_MAPPING_FILE_NAME 
        df = pd.DataFrame(data=Device.get_all_names(), columns=[DEVICE])
        df.to_csv(file_path, sep=',', index_label='id') 

    def create_activity_mapping_file(self):
        """ creates an activity mapping file with the current selected activities
            for logging. 

        Example
            id,activities
            0,eat
            1,sleep
        """

        from backend.models import Activity
        file_path = self.path_to_folder + settings.ACTIVITY_MAPPING_FILE_NAME
        df = pd.DataFrame(data=Activity.get_all_names(), columns=[ACTIVITY])
        df.to_csv(file_path, sep=',', index_label='id')


    def load_devices(self):
        from pyadlml.dataset._datasets.activity_assistant import _read_devices
        return _read_devices(
            self.path_to_folder + settings.DATA_FILE_NAME,
            self.path_to_folder + settings.DATA_MAPPING_FILE_NAME
        )

    def load_activity_mapping(self, as_dict=False):
        mapping = pd.read_csv(self.get_activity_map_fp())
        if not as_dict:
            return mapping
        else:
            return {v: k for k, v  in mapping.set_index('id').to_dict()[ACTIVITY].items()}




    def load_data_file(self):
        from pyadlml.dataset._datasets.activity_assistant import _read_devices
        return _read_devices(
            self.path_to_folder + settings.DATA_FILE_NAME,
            self.path_to_folder + settings.DATA_MAPPING_FILE_NAME
        )

    def load_device_mapping(self, as_dict=False):
        fp = self.path_to_folder + settings.DATA_MAPPING_FILE_NAME
        if as_dict:
            return pd.read_csv(fp, index_col=DEVICE).to_dict()['id']
        else:
            return pd.read_csv(fp, index_col='id').to_dict()[DEVICE]

    def get_persons_from_folder(self) -> list:
        person_list = []
        for fn in Path(self.path_to_folder).iterdir():
            if 'activities_subject_' in str(fn):
                person_list.append(str(fn).split('activities_subject_')[1][:-4])
        return person_list

        


    def delete(self, *args, **kwargs):
        """ perform additional cleanup when deleting a dataset
        """
        import shutil 
        # cleanup the mediafiles/plots associated with the person statistics and dataset
        try:
            shutil.rmtree(settings.MEDIA_ROOT + self.name)
        except FileNotFoundError:
            pass
        # Cleanup the dataset in /data/datasets/[name]
        try:
            shutil.rmtree(self.path_to_folder)
        except FileNotFoundError:
            pass
                       
        super().delete(*args, **kwargs) 

    def get_fileResponse(self):
        """ zips the dataset and returns a fileResponse object that is served to the user
        Returns
        -------
        fp : FileResponse
            a reponse object that servers a ZIP file
        """
        # create zip at location
        path_to_zip = settings.MEDIA_ROOT + self.name + ".zip"
        create_zip(self.path_to_folder, path_to_zip)

        # create response
        zip_file = open(path_to_zip, 'rb')
        response = FileResponse(zip_file)

        # cleanup zip file
        rem_file = pathlib.Path(path_to_zip)
        rem_file.unlink()
        return response

