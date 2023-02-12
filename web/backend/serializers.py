from asyncio import Handle
from rest_framework import serializers
from backend.models import *
from django.contrib.auth.models import User


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
        fields = ('server_address', 'setup', 'time_zone',
                  'hass_api_token', 'hass_db_url', 'hass_comp_installed',
                  'selected_model', 'realtime_node', 'dataset',
                  'poll_interval', 'is_polling',
                  'zero_conf_pid', 'poll_service_pid', 'plot_gen_service_pid',
                  'webhook_count')

#class PersonStatisticSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = PersonStatistic
#        fields = ('id', 'name', 'dataset', 'person', 'plot_hist_counts',
#            'num_activities', 'num_recorded_activities',
#            'plot_hist_cum_duration', 'plot_boxplot_duration',
#            'plot_ridge_line', 'plot_heatmap_transitions'
#            )

class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    # The many-to-one realtionship with Personstatistic is realized via the related-name
    # of field dataset in personstatistic. (google reverse relations for further information)
    class Meta:
        model = Dataset
        fields = ('id', 'name', 'path_to_folder', 'start_time', 'end_time',
            'num_devices', 'num_recorded_events', 'num_persons', 'num_activities', 'num_recorded_activities',
            'data_size',
        )


#class ModelSerializer(serializers.HyperlinkedModelSerializer):
#    class Meta:
#        model = Model
#        fields = ('id', 'person', 'dataset', 'file', 'datainstance',
#                  'train_loss', 'train_loss_graph', 'benchmark')

class ActivitySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Activity
        fields = ('id', 'name', 'areas')


class AreaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Area
        #fields = ['id', 'name', 'x', 'y', 'node_id', 'activities', 'devices']
        fields = ['id', 'name', 'activities', 'devices']


class EdgeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Edge
        fields = ('id', 'source', 'sink', 'distance')


class SmartphoneSerializer(serializers.HyperlinkedModelSerializer):
#class SmartphoneSerializer(serializers.HyperlinkedModelSerializer):
    #owner = serializers.ReadOnlyField(source='owner.username')
    person = serializers.HyperlinkedRelatedField(
            view_name='person-detail',
            allow_null=False,
            many=False,
            queryset=Person.objects.all())
    class Meta:
        model = Smartphone
        fields = ['id', 'name', 'person', 'logging',
                'logged_activity', 'synchronized']

class DeviceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Device
        fields = ['id', 'name', 'friendly_name', 'area']

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
        fields = ('id', 'name', 'hass_name', 'prediction',
                 'smartphone', 'activity_file')
                #'synthetic_activities')

#class UserSerializer(serializers.HyperlinkedModelSerializer):
#    persons = serializers.PrimaryKeyRelatedField(many=True, queryset=Person.objects.all())
#
#    class Meta:
#        model = User
#        fields = ('id', 'username', 'persons')
