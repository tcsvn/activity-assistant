# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DATA_FOLDER = '/home/data'
import os
import sys
sys.path.append(os.path.realpath('.')) # append path for imports
MEDIA_ROOT = DATA_FOLDER + '/media/'
HASSBRAIN_ACT_FILE_FOLDER = DATA_FOLDER + "/activity_logs"
HASSBRAIN_MODEL_FOLDER = DATA_FOLDER + "/models"


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_FOLDER + 'db.sqlite3',
    }
}


# Files like datasets and stuff
HASSBRAIN_ALGO_CONFIG = "/home/cmeier/code/hassbrain_web/hassbrain_rest/dev/conf_hassbrain_algorithm.yaml"
HASSBRAIN_PATH_TO_RT_MAIN = "/home/cmeier/code/hassbrain_web/hassbrain_rest/rt_node_main.py"


FILE_PATH_FIELD_DIRECTORY = "asdf"
MODEL_PATH_FIELD_DIRECTORY = "asdf"
