from backend.models import *
from backend.serializers import * 
from backend.permissions import IsOwnerOrReadOnly
from rest_framework import generics
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework import renderers
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.shortcuts import render
from act_assist import settings
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'



class ServerViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Server.objects.all()
    serializer_class = ServerSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    #def perform_create(self, serializer):
    #    serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        pass

class SyntheticActivityViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = SyntheticActivity.objects.all()
    serializer_class = SyntheticActivitySerializer

class ActivityPredictionViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = ActivityPrediction.objects.all()
    serializer_class = ActivityPredictionSerializer


class DevicePredictionViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = DevicePrediction.objects.all()
    serializer_class = DevicePredictionSerializer


class RealTimeNodeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = RealTimeNode.objects.all()
    serializer_class = RealTimeNodeSerializer

class DatasetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    #def perform_destroy(self, instance):
    #    instance.delete()


    #def perform_create(self, serializer):
    #    serializer.save(owner=self.request.user)

class ModelViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Model.objects.all()
    serializer_class = ModelSerializer
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    def perform_destroy(self, instance):
        """
        also deletes the model file associated with the model
        :param instance:
        :return:
        """
        instance.file.delete()
        instance.delete()


#from django.db.models.signals import post_delete
#from django.dispatch import receiver
#
#
#class MyModel(models.Model):
#    """Model containing file field"""
#    file = models.FileField(upload_to='somewhere', blank=False)
#    ...
#
#@receiver(post_delete, sender=MyModel)
#def submission_delete(sender, instance, **kwargs):
#    instance.file.delete(False)

    #def perform_create(self, serializer):
    #    serializer.save(owner=self.request.user)

class SmartphoneViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = Smartphone.objects.all()
    serializer_class = SmartphoneSerializer

    # for not auth, only allow get
    # for authenticated allow everything
    #permission_classes = (
    #        permissions.IsAuthenticated,
    #                    )
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    #@action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    #def highlight(self, request, *args, **kwargs):
    #    snippet = self.get_object()
    #    return Response(snippet.highlighted)

    def perform_update(self, serializer):
        """
        """
        prae_update_log = serializer.instance.logging # type: bool
        prae_update_act = serializer.instance.logged_activity
        instance = serializer.save()
        post_update_log = instance.logging
        post_update_act = instance.logged_activity

        #print('~'*100)
        #print('prae_update_log: ', prae_update_log)
        #print('prae_update_loc: ', prae_update_loc)
        #print('prae_update_act: ', prae_update_act)
        #print('post_update_log: ', post_update_log)
        #print('post_update_loc: ', post_update_loc)
        #print('post_update_act: ', post_update_act)
        #print('--')

    #def perform_create(self, serializer):
    #    #serializer.save(owner=self.request.user)
    #    serializer.save()



# api related stuff
class ActivityViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,)
       # IsOwnerOrReadOnly, )

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def flag_all_smartphones_unsyc(self):
        smartphones = Smartphone.objects.all()
        for phone in smartphones:
            phone.synchronized = False
            phone.save()

    # hook into the destroy process
    def perform_destroy(self, instance):
        #self.flag_all_smartphones_unsyc()
        instance.delete()

    def perform_create(self, serializer):
        #self.flag_all_smartphones_unsyc()
        #serializer.save(owner=self.request.user)
        serializer.save()


class EdgeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Edge.objects.all()
    serializer_class = EdgeSerializer
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    #def perform_destroy(self, instance):
    #    instance.delete()


    #def perform_create(self, serializer):
    #    serializer.save(owner=self.request.user)


class LocationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def flag_all_smartphones_unsyc(self):
        smartphones = Smartphone.objects.all()
        for phone in smartphones:
            phone.synchronized = False
            phone.save()

    def perform_destroy(self, instance):
        self.flag_all_smartphones_unsyc()
        instance.delete()


    def perform_create(self, serializer):
        self.flag_all_smartphones_unsyc()
        serializer.save(owner=self.request.user)

class DeviceViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        #serializer.save(owner=self.request.user)
        serializer.save()

class PersonViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Additionally we also provide an extra `highlight` action.
    """
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,)
        #IsOwnerOrReadOnly, )

    def perform_update(self, serializer):
        """ when updating activity file, the file should be replaced

        Parameters
        ----------
        serializer : 
        """
        logger.error("~"*10)
        prae_act_file = serializer.instance.activity_file
        logger.error("before", prae_act_file)
        instance = serializer.save()
        post_act_file = instance.activity_file
        logger.error("after", post_act_file)
        logger.error("\n"*5)

#class UserViewSet(viewsets.ReadOnlyModelViewSet):
#    """
#    This viewset automatically provides `list` and `detail` actions.
#    """
#    queryset = User.objects.all()
#    serializer_class = UserSerializer
