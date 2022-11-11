from django.conf.urls import url, include
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from frontend import views
from rest_framework.schemas import get_schema_view

urlpatterns = []

urlpatterns += [
    path('', views.SetupView.as_view(), name='setup'),
    re_path(r'^dashboard/', views.DashboardView.as_view(), name='dashboard'),
    re_path(r'^person/[0-9]+', views.PersonView.as_view(), name='person'),
    re_path(r'^dataset/$', views.DatasetView.as_view(), name='dataset'),
    re_path(r'^webhook', views.WebhookView.as_view(), name='webhook'),
    re_path(r'^config/assign_activities2areas', views.AssignActivityView.as_view(), name='assign_activities'),
    re_path(r'^config/assign_devices2areas', views.AssignDeviceView.as_view(), name='assignment_device'),
    re_path(r'^config', views.ConfigView.as_view(), name='config'),
    re_path(r'^dataset/[0-9]+', views.DatasetAnalyticsView.as_view(), name='dataset_analytics'),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    #re_path(r'^activities/', views.ActivityView.as_view(), name='activity'),
    #re_path(r'^map', views.EditMapView.as_view(), name='map'),
    #re_path(r'^model_selection', views.ModelSelectionView.as_view(), name='model_selection'),
    #re_path(r'^model', views.ModelView.as_view(), name='model')
]
