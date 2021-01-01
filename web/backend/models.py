from django.db import models
from pygments.lexers import get_all_lexers
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
from pyadlml.dataset.activities import _create_activity_df
from django.core.files import File
from django.http import FileResponse
from backend.util import create_zip

logger = logging.getLogger(__name__)
#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from rest_framework.authtoken.models import Token

def person_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/activities_subject_<person.name>.csv
    return settings.ACTIVITY_FILE_NAME%(instance.name)

class OverwriteStorage(FileSystemStorage):
    ''' this is used to overwrite existing files in a put request
        for FileField cases as in Person and model
    '''
    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class Dataset(models.Model):
    # todo mark for deletion line below
    name = models.CharField(null=True, max_length=100)
    path_to_folder = models.CharField(null=True, max_length=100)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    num_devices = models.IntegerField(null=True)
    num_recorded_events = models.IntegerField(null=True)
    data_size = models.IntegerField(null=True)

    plot_hist_counts = models.ImageField(null=True)
    plot_hist_on_off = models.ImageField(null=True)
    plot_boxplot_on_duration = models.ImageField(null=True)
    plot_heatmap_trigger_one_day = models.ImageField(null=True)
    plot_heatmap_trigger_time = models.ImageField(null=True)
    plot_hist_trigger_time_diff = models.ImageField(null=True)
    plot_heatmap_cross_correlation = models.ImageField(null=True)

    def delete(self, *args, **kwargs):
        """ perform additional cleanup when deleting a dataset
        """
        import shutil 
        # cleanup the mediafiles/plots associated with the person statistics and dataset
        try:
            shutil.rmtree(settings.MEDIA_ROOT + self.name)
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


class PersonStatistic(models.Model):
    name = models.CharField(null=True, max_length=100)
    dataset = models.ForeignKey(Dataset, related_name="person_statistics", on_delete=models.CASCADE)
    activity_file = models.FileField(null=True) 
    num_activities = models.IntegerField(null=True)
    num_recorded_activities = models.IntegerField(null=True)   

    plot_hist_counts = models.ImageField(null=True)
    plot_hist_cum_duration = models.ImageField(null=True)
    plot_boxplot_duration = models.ImageField(null=True)
    plot_ridge_line = models.ImageField(null=True)
    plot_heatmap_transitions = models.ImageField(null=True)

    def get_activity_fp(self):
        """ returns filepath to activity file
        """
        return os.path.join(self.dataset.path_to_folder,
            settings.ACTIVITY_FILE_NAME%(self.name)
        )

class Person(models.Model):
    name = models.CharField(max_length=20, blank=True, default='')
    hass_name = models.CharField(max_length=20, blank=True, default='')
    person_statistic = models.OneToOneField(PersonStatistic, null=True, on_delete=models.SET_NULL, related_name='person')
    prediction = models.BooleanField(default=False, blank=True)
    activity_file = models.FileField(null=True, 
        upload_to=person_path, storage=OverwriteStorage()) 


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
    
    def reset_activity_file(self):
        """ creates inital and assigns activity file
        File looks like this
            start_time, end_time, activity
        """
        fp = settings.MEDIA_ROOT + settings.ACTIVITY_FILE_NAME%(self.name)
        output_dir = Path(settings.MEDIA_ROOT)
        output_dir.mkdir(parents=True, exist_ok=True)
        tmp = _create_activity_df()
        tmp.to_csv(fp, sep=',', index=False)
        self.activity_file = File(open(fp))
        self.save()

# A Location presents a vertice in a Graph 
# Graph := (G, E)
# v\in E
class Location(models.Model):
    node_id = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()
    name = models.CharField(max_length=40)

    class Meta:
        ordering = ["name"]

# an edge connects to locations with each other
# e  = (v,w) | v,w \in G
class Edge(models.Model):
    # if a node is deleted, the edge is also deleted
    source = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='source')
    sink = models.ForeignKey(Location, on_delete=models.CASCADE)
    distance = models.IntegerField(default=0)

    class Meta:
        ordering = ["source"]

# is something like a sensor, switch, or whatever
class Device(models.Model):
    name = models.CharField(max_length=40)
    #area = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)

#  many to one relation with person
# many persons can do the same activity, but a person can do  only one activity at once
class Activity(models.Model):
    name = models.CharField(max_length=40)
    #locations = models.ManyToManyField(Location, related_name='activities')

    class Meta:
        ordering = ["name"]


class ActivityPrediction(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE, related_name='predicted_activities')
    predicted_activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')
    score = models.FloatField()

class SyntheticActivity(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.CASCADE, related_name='synthetic_activities')
    #synthetic_activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')
    synthetic_activity = models.ForeignKey(Activity, null=False, blank=False, on_delete=models.CASCADE, related_name='%(class)s_predicted')
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
    person = models.OneToOneField(Person, blank=True, on_delete=models.CASCADE)#, primary_key=True)
    logging = models.BooleanField(default=False)
    synchronized = models.BooleanField(default=False)
    logged_activity = models.ForeignKey(Activity, null=True, on_delete=models.SET_NULL, related_name='%(class)s_logged')


class Model(models.Model):
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)

    # TODO rename file to sth more accurate
    file = models.FileField(null=True)
    visualization = models.ImageField(null=True)
    train_loss = models.FileField(null=True)
    train_loss_graph = models.ImageField(null=True)

class RealTimeNode(models.Model):
    pid = models.IntegerField(default=0)
    model = models.ForeignKey(Model, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, null=True)

class DevicePrediction(models.Model):
    rt_node = models.ForeignKey(RealTimeNode, blank=True, on_delete=models.CASCADE, related_name='predicted_devices')
    predicted_state = models.ForeignKey(Device, null=True, blank=True, on_delete=models.CASCADE, related_name='%(class)s_predicted')
    score = models.FloatField()

class Server(models.Model):
    server_address = models.CharField(max_length=40, null=True)
    hass_api_token = models.CharField(max_length=200, null=True)
    hass_comp_installed = models.BooleanField(default=False)
    selected_model = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL, related_name='model')
    realtime_node = models.ForeignKey(RealTimeNode, null=True, on_delete=models.SET_NULL)
    setup = models.CharField(max_length=10, null=True, default='step 0')
    is_polling = models.BooleanField(default=False)
    poll_interval = models.CharField(max_length=10, default='10m')
    dataset = models.ForeignKey(Dataset, null=True, blank=True, on_delete=models.CASCADE, related_name='synthetic_activities')
    zero_conf_pid = models.IntegerField(null=True)
    poll_service_pid = models.IntegerField(null=True)
    plot_gen_service_pid = models.IntegerField(null=True)
    time_zone = models.CharField(max_length=20, null=True)
    webhook_count = models.IntegerField(default=0)