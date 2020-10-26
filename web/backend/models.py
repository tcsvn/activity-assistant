from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.conf import settings
from django.contrib.auth.models import User
#from django.db.models.signals import post_save
#from django.dispatch import receiver
#from rest_framework.authtoken.models import Token



class Dataset(models.Model):
    name = models.CharField(max_length=40, null=True)
    class_name = models.CharField(max_length=40, null=True)
    # todo mark for deletion line below
    path_to_folder = models.FilePathField(null=True)

    class Meta:
        ordering = ["name"]

# generate token for every new created user
#@receiver(post_save, sender=settings.AUTH_USER_MODEL)
#def create_auth_token(sender, instance=None, created=False, **kwargs):
#        if created:
#                    Token.objects.create(user=instance)
class DataInstance(models.Model):
    name = models.CharField(max_length=40, null=False)
    dataset = models.ForeignKey(Dataset, null=False, on_delete=models.CASCADE)
    data_rep = models.CharField(max_length=40, null=False)
    timeslicelength = models.CharField(max_length=40, null=False)
    test_sel = models.CharField(max_length=40, null=True)
    data_file = models.FileField(null=True)

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

class DeviceComponent(models.Model):
    """
    examples: switch, sensor, binary_sensor, ...
    """
    name = models.CharField(max_length=40)

# is something like a sensor, switch, or whatever
class Device(models.Model):
    name = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    # the type of the state 
    # examples: boolean, float, ...
    component = models.ForeignKey(DeviceComponent, on_delete=models.CASCADE)
    # if a component is deleted also delete all the devices that adhere to that component

#  many to one relation with person
# many persons can do the same activity, but a person can do  only one activity at once
class Activity(models.Model):
    name = models.CharField(max_length=40)
    locations = models.ManyToManyField(Location, related_name='activities')

    class Meta:
        ordering = ["name"]

class Person(models.Model):
    #owner = models.ForeignKey('auth.User', related_name='persons', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default='')
    prediction = models.BooleanField(default=False, blank=True)
    """
    todo feature
    predictions is either 'running', 'enabled' or 'disabled'
    """
    #prediction = models.CharField(max_length=10, default='disabled', blank=True)
    #predicted_activity = models.ForeignKey(Activity, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')
    #predicted_activity = models.OneToMany(ActivityPrediction, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')
    predicted_location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL, related_name='%(class)s_predicted')

    def save(self, *args, **kwargs):
        # create additional user with one to one relationship so that
        # one device can't alter the anything but its own person
        #User.objects.create_user(username=self.name, email='test@test.de', password='test')
        super(Person, self).save(*args, **kwargs)

    class Meta:
        ordering = ('created',)


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



# is the connected data logger
# there can be persons without smartphone
# there can be no smartphone without a person
# access smartphone via person: person.smartphone <Smarpthone: nexus5>
class Smartphone(models.Model):
    owner = models.ForeignKey('auth.User', related_name='smartphones', on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    logging = models.BooleanField(default=False)
    logged_activity = models.ForeignKey(Activity, null=True, on_delete=models.SET_NULL, related_name='%(class)s_logged')
    logged_location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL, related_name='%(class)s_logged')
    synchronized = models.BooleanField(default=False)

    # if a person is deleted so should the smartphone
    person = models.OneToOneField(Person, blank=True, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        ordering = ["name"]

class Algorithm(models.Model):
    name = models.CharField(max_length=40, blank=True)
    class_name = models.CharField(max_length=40, blank=True)
    description = models.TextField(max_length=500, blank=True)

    selected_person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.SET_NULL)
    selected_dataset = models.ForeignKey(Dataset, null=True, on_delete=models.SET_NULL, related_name='selected_dataset')

    compatible_dataset = models.ManyToManyField(Dataset,
                                       related_name='compatible_dataset')
    multiple_person = models.BooleanField(default=False)
    unsupervised = models.BooleanField(default=False)
    synthetic_activities = models.BooleanField(default=False)
    location = models.BooleanField(default=False)
    duration = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

class ModelComparision(models.Model):
    pass

class Model(models.Model):
    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    """
    null is true because a model can be trained upon a dataset like kasteren or mavlab without
    the association of a person
    """
    person = models.ForeignKey(Person, null=True, on_delete=models.CASCADE)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='dataset')
    datainstance = models.ForeignKey(DataInstance, null=False, on_delete=models.CASCADE, related_name='datainstance')

    # todo rename file to sth more accurate
    file = models.FileField(null=True)
    visualization = models.ImageField(null=True)
    train_loss = models.FileField(null=True)
    train_loss_graph = models.ImageField(null=True)

class Benchmark(models.Model):
    model = models.OneToOneField(
        Model,
        on_delete=models.CASCADE,
        primary_key=True)

    df_conf_mat = models.FileField(null=True)
    df_metrics = models.FileField(null=True)
    df_class_acts = models.FileField(null=True)
    img_feature_importance = models.ImageField(null=True)
    img_act_dur_dists = models.ImageField(null=True)
    img_inf_states = models.ImageField(null=True)




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
    hass_address = models.CharField(max_length=40, null=True)
    hass_api_token = models.CharField(max_length=200, null=True)
    selected_model = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL, related_name='model')
    selected_algorithm = models.ForeignKey(Algorithm, null=True, on_delete=models.SET_NULL, related_name='algorithm')
    selected_dataset = models.ForeignKey(Dataset, null=True, on_delete=models.SET_NULL)
    realtime_node = models.ForeignKey(RealTimeNode, null=True, on_delete=models.SET_NULL)

