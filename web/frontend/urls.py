from django.conf.urls import url, include
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from frontend import views
from rest_framework.schemas import get_schema_view

urlpatterns = []


urlpatterns += [
    path('', views.DashboardView.as_view(), name='dashboard'),
    re_path(r'^person/[0-9]+', views.PersonView.as_view(), name='person'),
    re_path(r'^basic', views.BasicConfig.as_view(), name='basic_config'),
    re_path(r'^create_person', views.CreatePersonView.as_view(), name='create_person'),
    re_path(r'^activities/', views.ActivityView.as_view(), name='activity'),
    re_path(r'^map', views.EditMapView.as_view(), name='map'),
    re_path(r'^assign_sensors', views.AssignSensor.as_view(), name='assign_sensors'),
    re_path(r'^assign_activities_to_locations', views.AssignActivities.as_view(), name='assign_activities'),
    re_path(r'^algorithms', views.AlgorithmView.as_view(), name='algorithms'),
    re_path(r'^model_selection', views.ModelSelectionView.as_view(), name='model_selection'),
    re_path(r'^model', views.ModelView.as_view(), name='model')
]
