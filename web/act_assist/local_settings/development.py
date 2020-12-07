import os
import sys
sys.path.append(os.path.realpath('.'))
#from settings import DATA_ROOT

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ZERO_CONF_MAIN_PATH = "/share/zero_conf_server.py"
UPDATER_SERVICE_PATH = "/share/dataset_updater_service.py"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    '/home/hassbrain_rest/frontend/static/',
]