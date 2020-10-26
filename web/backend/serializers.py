from rest_framework import serializers
from backend.models import *
from django.contrib.auth.models import User


class DataInstanceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataInstance
        fields = ('id', 'name', 'dataset', 'data_rep', 'timeslicelength', 'test_sel', 'data_file')

class SyntheticActivitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SyntheticActivity
        fields = ('id', 'person', 'synthetic_activity', 'day_of_week', 'start', 'end')

class ActivityPredictionSerializer(serializers.HyperlinkedModelSerializer):
    #person = serializers.HyperlinkedRelatedField(
    #    view_name='person-detail',
    #    allow_null=False,
    #    many=False,
    #    queryset=Person.objects.all())

    class Meta:
        model = ActivityPrediction
        fields = ('id', 'person', 'predicted_activity', 'score')

class DevicePredictionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DevicePrediction
        fields = ('id', 'rt_node', 'predicted_state', 'score')

class RealTimeNodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RealTimeNode
        fields = ('id', 'pid', 'status', 'model', 'predicted_devices')

class ServerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Server
        fields = ('hass_address', 'server_address', 'hass_api_token',
                  'selected_model', 'selected_algorithm', 'selected_dataset', 'realtime_node')

class DatasetSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Dataset
        fields = ('id', 'name', 'class_name', 'path_to_folder')

class ModelSerializer(serializers.HyperlinkedModelSerializer):
    benchmark = serializers.HyperlinkedRelatedField(
            view_name='benchmark-detail',
            allow_null=True,
            many=False,
            queryset=Benchmark.objects.all())
    class Meta:
        model = Model
        fields = ('id', 'algorithm', 'person', 'dataset', 'file', 'visualization', 'datainstance',
                  'train_loss', 'train_loss_graph', 'benchmark')

class BenchmarkSerializer(serializers.HyperlinkedModelSerializer):
    model = serializers.HyperlinkedRelatedField(
            view_name='model-detail',
            allow_null=False,
            many=False,
            queryset=Model.objects.all())
    class Meta:
        model = Benchmark
        fields = ('model', 'df_conf_mat', 'df_metrics', 'df_class_acts', 'img_feature_importance',
                  'img_act_dur_dists', 'img_inf_states')

class AlgorithmSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Algorithm
        fields = ('id', 'name', 'class_name', 'description', 'compatible_dataset',
                  'selected_person', 'selected_dataset',
                  'multiple_person', 'unsupervised', 'synthetic_activities',
                  'location', 'duration')

class ActivitySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Activity
        fields = ('id', 'name', 'locations')


class LocationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Location
        fields = ('id', 'name', 'x', 'y', 'node_id', 'activities')


class EdgeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Edge 
        fields = ('id', 'source', 'sink', 'distance')


class SmartphoneSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    person = serializers.HyperlinkedRelatedField(
            view_name='person-detail',
            allow_null=False,
            many=False, 
            queryset=Person.objects.all())
    class Meta:
        model = Smartphone
        fields = ('name', 'owner', 'person', 'logging', 
                'logged_activity', 'logged_location', 'synchronized')

class DeviceComponentSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = DeviceComponent
        fields = ('id', 'name')


class DeviceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Device
        fields = ('id', 'name', 'location', 'component', 'state')
        #fields = ('id', 'name', 'location', 'state')

class PersonSerializer(serializers.HyperlinkedModelSerializer):
    #owner = serializers.ReadOnlyField(source='owner.username')
    smartphone = serializers.HyperlinkedRelatedField(
            view_name='smartphone-detail',
            allow_null=True,
            many=False, 
            queryset=Smartphone.objects.all())
#    owner_device = serializers.ReadOnlyField(source='owner_device.username')
    #highlight = serializers.HyperlinkedIdentityField(view_name='person-highlight', format='html')

    class Meta:
        model = Person
        fields = ('id', 'name', 'prediction',
                'smartphone',
                'predicted_location',
                'predicted_activities',
                'synthetic_activities')

#class UserSerializer(serializers.HyperlinkedModelSerializer):
#    persons = serializers.PrimaryKeyRelatedField(many=True, queryset=Person.objects.all())
#
#    class Meta:
#        model = User
#        fields = ('id', 'username', 'persons')
