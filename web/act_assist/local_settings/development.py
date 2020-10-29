import os
import sys

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DATA_FOLDER = '/media/activity_assistant'

sys.path.append(os.path.realpath('.')) # append path for imports
MEDIA_ROOT = DATA_FOLDER + '/media/'
HASSBRAIN_ACT_FILE_FOLDER = DATA_FOLDER + "/activity_logs"
HASSBRAIN_MODEL_FOLDER = DATA_FOLDER + "/models"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_FOLDER + '/db.sqlite3',
    }
}


# Files like datasets and stuff
HASSBRAIN_ALGO_CONFIG = "NotImplemented"
HASSBRAIN_PATH_TO_RT_MAIN = "NotImplemented"

FILE_PATH_FIELD_DIRECTORY = "NotImplemented"
MODEL_PATH_FIELD_DIRECTORY = "NotImplemented"