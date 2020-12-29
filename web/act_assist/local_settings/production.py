import sys
import os

SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'
#SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

DEBUG = False

STATIC_ROOT = '/var/cache/activity_assistant/static/'
STATICFILES_DIRS = ['/opt/activity_assistant/web/frontend/static']

ZERO_CONF_MAIN_PATH = "/opt/activity_assistant/zero_conf_server.py"
UPDATER_SERVICE_PATH = "/opt/activity_assistant/dataset_updater_service.py"
PLOT_GEN_SERVICE_PATH = "/opt/activity_assistant/plot_generator_service.py"