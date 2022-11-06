import django
from django.conf.urls import url, include
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from backend import views
import settings


router = DefaultRouter()
router.register(settings.URL_SERVER, views.ServerViewSet)
#router.register(r'realtimenode', views.RealTimeNodeViewSet)
#router.register(set.URL_DEVICE_PREDICTIONS, views.DevicePredictionViewSet)
#router.register(set.URL_ACTIVITY_PREDICTIONS, views.ActivityPredictionViewSet)
#router.register(set.URL_SYNTHETIC_ACTIVITY, views.SyntheticActivityViewSet)
router.register(r'persons', views.PersonViewSet)
router.register(r'personStatistics', views.PersonStatisticViewSet)
#router.register(r'users', views.UserViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'devices', views.DeviceViewSet)
#router.register(r'models', views.ModelViewSet)
router.register(r'datasets', views.DatasetViewSet)
router.register(r'smartphones', views.SmartphoneViewSet)
router.register(r'areas', views.AreaViewSet)
#router.register(r'edges', views.EdgeViewSet)
urlpatterns = []


urlpatterns += [
    url(r'^%s/'%(settings.REST_API_URL), include(router.urls)),
]


# add coreapi suppoert
schema_view = get_schema_view(title=settings.REST_API_TITLE)
urlpatterns+=[
   url(r'^%s/schema/$'%(settings.REST_API_URL), schema_view),
]

# add auth support
urlpatterns += [
    url(r'^%s/auth/'%(settings.REST_API_URL), include('rest_framework.urls')),
]

# serve media
# models can be downloaded
if settings.SERVE_MEDIA:
    urlpatterns += [
       url(r'^media/(?P<path>.*)$', django.views.static.serve,
           {'document_root': settings.MEDIA_ROOT}),
    ]
