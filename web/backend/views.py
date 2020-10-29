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
    permission_classes = (
            permissions.IsAuthenticated,
                        )
    #permission_classes = (
    #    permissions.IsAuthenticatedOrReadOnly,
    #    IsOwnerOrReadOnly, )

    #@action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    #def highlight(self, request, *args, **kwargs):
    #    snippet = self.get_object()
    #    return Response(snippet.highlighted)

    def _create_folder_if_not_exits(self, person):
        """ if the folder with the person does not exist create the folder and return the path
        :param person:
        :return:
        """
        person_path = settings.HASSBRAIN_ACT_FILE_FOLDER + "/" + str(person.name)
        import os
        if not os.path.exists(person_path):
            os.makedirs(person_path)
        return person_path

    def _create_file_if_not_exists(self, path_to_folder):
        # create file if it not exists
        file_path = path_to_folder + "/" + settings.ACTIVITY_FILE_NAME
        from pathlib import Path
        act_file = Path(file_path)
        if not act_file.is_file():
            open(file_path, 'a').close()
        return file_path


    def _only_location_has_changed(self, prae_change_log, post_change_log, prae_change_loc,
                                   post_change_loc, prae_change_act, post_change_act):
        """
        the case when only the location was changed which doesn't concern us at the moment
        """
        return prae_change_log == post_change_log and prae_change_loc != post_change_loc \
                and prae_change_act == post_change_act

    def _logging_turned_on(self, prae_update_log, post_update_log):
        """case:   logging button was turned on and no logging activity preceeded the action """
        return prae_update_log != post_update_log and post_update_log == True


    def _diff_activity_selected(self, prae_update_act, post_update_act, post_update_log):
        """case:   if the activity changed """
        return prae_update_act != post_update_act and post_update_log == True

    def _logging_turned_off(self, prae_update_log, post_update_log):
        return prae_update_log == True and post_update_log == False

    def perform_update(self, serializer):
        prae_update_log = serializer.instance.logging # type: bool
        prae_update_loc = serializer.instance.logged_location
        prae_update_act = serializer.instance.logged_activity
        instance = serializer.save()
        post_update_log = instance.logging
        post_update_loc = instance.logged_location
        post_update_act = instance.logged_activity

        if prae_update_log == False and post_update_log == False:
            return

        if self._only_location_has_changed(prae_update_log, post_update_log, prae_update_loc,
                                           post_update_loc, prae_update_act, post_update_act):
            return

        #print('~'*100)
        #print('prae_update_log: ', prae_update_log)
        #print('prae_update_loc: ', prae_update_loc)
        #print('prae_update_act: ', prae_update_act)
        #print('post_update_log: ', post_update_log)
        #print('post_update_loc: ', post_update_loc)
        #print('post_update_act: ', post_update_act)
        #print('--')

        person_path = self._create_folder_if_not_exits(instance.person)
        file_path = self._create_file_if_not_exists(person_path)
        import hassbrain_rest.backend.activity_logger as activity_logger
        # todo debug remove line below
        if self._logging_turned_on(prae_update_log, post_update_log):

            activity_logger.create_new_act_entry(file_path, post_update_act.name)

        elif self._diff_activity_selected(prae_update_act, post_update_act, post_update_log):
            """
            action: create two log entrys: 
                the first finishes the current activity 
                then next starts the next
            """
            import time
            try:
                activity_logger.finish_existing_act_entry(file_path, prae_update_act.name)
            except AssertionError:
                # the case when an activity couldn't be finished because of mismatch of names
                activity_logger.delete_last_row(file_path)

            time.sleep(1)
            activity_logger.create_new_act_entry(file_path, post_update_act.name)

        elif self._logging_turned_off(prae_update_log, post_update_log):
            """
            case:   if the logging was turned off but no activity was changed
            action: finish the current activity 
            """
            try:
                activity_logger.finish_existing_act_entry(file_path, post_update_act.name)
            except AssertionError:
                # the case when an activity couldn't be finished because of mismatch of names
                activity_logger.delete_last_row(file_path)

        #print('~'*100)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



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
        self.flag_all_smartphones_unsyc()
        instance.delete()

    def perform_create(self, serializer):
        self.flag_all_smartphones_unsyc()
        serializer.save(owner=self.request.user)


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

    #@action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    #def highlight(self, request, *args, **kwargs):
    #    snippet = self.get_object()
    #    return Response(snippet.highlighted)

    def _create_activity_file_if_not_exists(self, folder_path):
        # create file if it not exists
        file_path = folder_path + "/" + settings.ACTIVITY_FILE_NAME
        from pathlib import Path
        act_file = Path(file_path)
        if not act_file.is_file():
            open(file_path, 'a').close()

    def _create_activity_folder_if_not_exists(self, folder_path):
        # if the folder for the person to log the activities to does not exits, create one
        import os
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    def perform_create(self, serializer):
        serializer.save()
        instance = serializer.instance

        person_path = settings.HASSBRAIN_ACT_FILE_FOLDER + "/" + str(instance.name)
        print('person_path: ', person_path)
        self._create_activity_folder_if_not_exists(person_path)
        self._create_activity_file_if_not_exists(person_path)


#class UserViewSet(viewsets.ReadOnlyModelViewSet):
#    """
#    This viewset automatically provides `list` and `detail` actions.
#    """
#    queryset = User.objects.all()
#    serializer_class = UserSerializer
