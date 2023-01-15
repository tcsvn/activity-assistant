from django.db import models
import shutil
from hass_api.rest import HARest
from pygments.lexers import get_all_lexers
from pyadlml.constants import TIME, DEVICE, VALUE, START_TIME, END_TIME, ACTIVITY
import pandas as pd
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import os
import logging
from pathlib import Path
import pathlib
from pyadlml.dataset._core.activities import create_empty_activity_df
from django.core.files import File
from django.http import FileResponse
from backend.util import create_zip

logger = logging.getLogger(__name__)
#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from rest_framework.authtoken.models import Token


def person_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/activities_subject_<person.name>.csv
    return settings.ACTIVITY_FILE_NAME % (instance.name)


class OverwriteStorage(FileSystemStorage):
    ''' this is used to overwrite existing files in a put request
        for FileField cases as in Person and model
    '''

    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


# class PersonStatistic(models.Model):
#    from .dataset import Dataset
#    name = models.CharField(null=True, max_length=100)
#    dataset = models.ForeignKey(Dataset, related_name="person_statistics", on_delete=models.CASCADE)
#    activity_file = models.FileField(null=True)
#    num_activities = models.IntegerField(null=True)
#    num_recorded_activities = models.IntegerField(null=True)
#
#    plot_hist_counts = models.ImageField(null=True)
#    plot_hist_cum_duration = models.ImageField(null=True)
#    plot_boxplot_duration = models.ImageField(null=True)
#    plot_ridge_line = models.ImageField(null=True)
#    plot_heatmap_transitions = models.ImageField(null=True)
#
#    def get_activity_fp(self):
#        """ returns filepath to activity file
#        """
#        return os.path.join(self.dataset.path_to_folder,
#            settings.ACTIVITY_FILE_NAME%(self.name)
#        )

class Person(models.Model):
    name = models.CharField(max_length=20, blank=True, default='')
    hass_name = models.CharField(max_length=20, blank=True, default='')
    #person_statistic = models.OneToOneField(PersonStatistic, null=True, on_delete=models.SET_NULL, related_name='person')
    prediction = models.BooleanField(default=False, blank=True)
    activity_file = models.FileField(null=True,
                                     upload_to=person_path, storage=OverwriteStorage())

    @classmethod
    def get_all_names(cls):
        return list(Person.objects.all().values_list('name', flat=True))

    @classmethod
    def get_all_ha_names(cls):
        return list(Person.objects.all().values_list('hass_name', flat=True))

    def save(self, *args, **kwargs):
        # create additional user with one to one relationship so that
        # one device can't alter the anything but its own person
        #User.objects.create_user(username=self.name, email='test@test.de', password='test')
        super(Person, self).save(*args, **kwargs)

        # check if there is a file attached to person if not create empty one
        try:
            self.activity_file.path
        except ValueError:
            self.reset_activity_file()

    def reset_smartphone(self):
        """ Mark smartphone if connected to person dirty
        """
        if hasattr(self, 'smartphone') and self.smartphone is not None:
            self.smartphone.synchronized = False
            self.smartphone.save()


    def reset_activity_file(self):
        """ creates inital and assigns activity file
        File looks like this
            start_time, end_time, activity
        """
        fp = settings.MEDIA_ROOT + settings.ACTIVITY_FILE_NAME % (self.name)
        output_dir = Path(settings.MEDIA_ROOT)
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = create_empty_activity_df()
        tmp.to_csv(fp, sep=',', index=False)
        self.activity_file = File(open(fp))
        self.save()

    def get_activity_file_fp(self) -> Path:
        return Path(settings.MEDIA_ROOT).joinpath(self.activity_file.name)

    def collect_from_ha_tracker(self):
        if hasattr(self, 'hatracker'):
            self.hatracker.transform_activity_df()

    def remap_activity_file(self, mapping, inplace=True):
        self.activity_file.close()
        fp = self.activity_file.path
        df_acts = pd.read_csv(fp, sep=',')
        df_acts[ACTIVITY] = df_acts[ACTIVITY].map(mapping)
        if inplace:
            df_acts.to_csv(fp, sep=',', index=False)
        else:
            return df_acts


# A Location presents a vertice in a Graph
# Graph := (G, E)
# v\in E
class Area(models.Model):
    #node_id = models.IntegerField()
    #x = models.IntegerField()
    #y = models.IntegerField()
    name = models.CharField(max_length=40)

    @classmethod
    def get_all_names(cls):
        return list(Area.objects.all().values_list('name', flat=True))

    @classmethod
    def by_name(cls, name):
        res = Area.objects.get(name=name)
        return res

    def save(self, *args, **kwargs):
        for area in Area.objects.all():
            if area.name == self.name:
                return

        return super(Area, self).save(*args, **kwargs)

    class Meta:
        ordering = ["name"]

# an edge connects to locations with each other
# e  = (v,w) | v,w \in G


class Edge(models.Model):
    # if a node is deleted, the edge is also deleted
    source = models.ForeignKey(
        Area, on_delete=models.CASCADE, related_name='source')
    sink = models.ForeignKey(Area, on_delete=models.CASCADE)
    distance = models.IntegerField(default=0)

    class Meta:
        ordering = ["source"]


class Device(models.Model):
    name = models.CharField(max_length=100)
    friendly_name = models.CharField(max_length=20)
    area = models.ForeignKey(
        Area, null=True, on_delete=models.SET_NULL, related_name='devices')

    @classmethod
    def get_all_names(cls):
        return list(Device.objects.all().values_list('name', flat=True))

    @classmethod
    def by_name(cls, name):
        return Device.objects.get(name=name)

    @classmethod
    def get_friendly_name_mapping(cls, name_list=[], names_as_key=False) -> dict:
        """ Create a map of either device or device name to friendly name from HA.
            If no friendly name exists the device name is substituted
        """
        if (isinstance(name_list, list) and not name_list):
            name_list = Device.get_all_names()
        mapping = HARest().get_friendly_names(name_list)
        res_map = {}
        for name, frname in mapping.items():
            new_key = name if names_as_key else Device.by_name(name)
            frname = name if frname is None else frname 
            res_map[new_key] = frname

        return mapping

    @classmethod
    def getCountAssignedDevices(cls):
        device_list = Device.objects.all()
        if device_list == []:
            return 0
        counter = 0
        for device in device_list:
            if device.area != None:
                counter += 1
        return counter

    def update_friendly_name(self):
        frname = HARest().get_friendly_name(self.name)
        self.friendly_name = frname if frname is not None else self.name
        self.save()


# Many to one relation with person
# Many persons can do the same activity, but a person can do  only one activity at once
class Activity(models.Model):
    name = models.CharField(max_length=40)
    areas = models.ManyToManyField(Area, related_name='activities')

    class Meta:
        ordering = ["name"]

    @classmethod
    def get_all_names(cls):
        return list(Activity.objects.all().values_list('name', flat=True))


class ActivityPrediction(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True,
                               on_delete=models.CASCADE, related_name='predicted_activities')
    predicted_activity = models.ForeignKey(
        Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')
    score = models.FloatField()


class SyntheticActivity(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True,
                               on_delete=models.CASCADE, related_name='synthetic_activities')
    #synthetic_activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')
    synthetic_activity = models.ForeignKey(
        Activity, null=False, blank=False, on_delete=models.CASCADE, related_name='%(class)s_predicted')
    # day of week (0 - 6) Sunday - Saturday
    day_of_week = models.IntegerField()
    start = models.TimeField()
    end = models.TimeField()


class Smartphone(models.Model):
    """ represents the android app installed on one smartphone
        there can be persons without smartphone
        there can be no smartphone without a person
    """
    #owner = models.ForeignKey('auth.User', related_name='smartphones', on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    # if a person is deleted so should the smartphone
    person = models.OneToOneField(
        Person, blank=True, on_delete=models.CASCADE)  # , primary_key=True)
    logging = models.BooleanField(default=False)
    synchronized = models.BooleanField(default=False)
    logged_activity = models.ForeignKey(
        Activity, null=True, on_delete=models.SET_NULL, related_name='%(class)s_logged')


class Model(models.Model):
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)
    file = models.FileField(null=True)


class RealTimeNode(models.Model):
    pid = models.IntegerField(default=0, primary_key=True)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, null=True)


class DevicePrediction(models.Model):
    rt_node = models.ForeignKey(
        RealTimeNode, blank=True, on_delete=models.CASCADE, related_name='predicted_devices')
    predicted_state = models.ForeignKey(
        Device, null=True, blank=True, on_delete=models.CASCADE, related_name='%(class)s_predicted')
    score = models.FloatField()


class Server(models.Model):
    from .dataset import Dataset
    #from .experiment import Experiment

    id = models.AutoField(primary_key=True)
    server_address = models.CharField(max_length=40, null=True)
    hass_api_token = models.CharField(max_length=200, null=True)
    hass_comp_installed = models.BooleanField(default=False)
    hass_db_url = models.CharField(max_length=200, null=True)

    selected_model = models.ForeignKey(
        Model, null=True, on_delete=models.SET_NULL, related_name='model')
    realtime_node = models.ForeignKey(
        RealTimeNode, null=True, on_delete=models.SET_NULL)

    setup = models.CharField(max_length=10, null=True, default='step 0')
    is_polling = models.BooleanField(default=False)
    poll_interval = models.CharField(max_length=10, default='10m')
    dataset = models.ForeignKey(Dataset, null=True, blank=True,
                                on_delete=models.CASCADE, related_name='synthetic_activities')
    #experiment = models.ForeignKey(Experiment, null=True, blank=True, on_delete=models.CASCADE)
    zero_conf_pid = models.IntegerField(null=True)
    poll_service_pid = models.IntegerField(null=True)
    plot_gen_service_pid = models.IntegerField(null=True)
    time_zone = models.CharField(max_length=20, null=True)
    webhook_count = models.IntegerField(default=0)

    def is_experiment_running(self):
        return not (self.dataset is None)

    def experiment_status(self):
        if self.dataset is None:
            return 'not_running'
        elif self.is_polling:
            return 'running'
        else:
            return 'paused'

    def refresh_hass_token(self):
        """ Saves the current env variable SUPERVISOR_TOKEN into
        """
        self.hass_api_token = os.environ.get('SUPERVISOR_TOKEN')
        self.save()

    def get_current_time(self):
        """ returns current time w.r.t to the timezone defined in
        Returns
        -------
        : str
            time string of now()
        """
        from datetime import datetime
        from web.frontend.util import utc_to_localtime
        if self.time_zone is None:
            time_zone = 'UTC'
        else:
            time_zone = self.time_zone
        return utc_to_localtime(datetime.utcnow(), time_zone)

    def get_address_port(self):
        return self.server_address.split(':')[-1]
