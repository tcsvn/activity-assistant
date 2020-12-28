import os
import sys
sys.path.append(os.path.realpath('.'))
from settings import BASE_DIR

SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'
DEBUG = True

STATIC_ROOT = '/share/web/frontend/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

ZERO_CONF_MAIN_PATH = "/share/services/zero_conf_server.py"
UPDATER_SERVICE_PATH = "/share/services/dataset_updater_service.py"
PLOT_GEN_SERVICE_PATH = "/share/services/plot_generator_service.py"