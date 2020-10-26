# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'

DEBUG = True

DATA_DIR = "/home/data"
# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DATA_DIR + '/database/db.sqlite3',
    }
}


# Files like datasets and stuff
HASSBRAIN_ALGO_CONFIG = "/home/conf_hassbrain_algorithm.yaml"

HASSBRAIN_MODEL_FOLDER = "/home/data/hb_models/"
HASSBRAIN_ACT_FILE_FOLDER = "/home/data/activity_logs/"
HASSBRAIN_DATASET_FOLDER = "/home/data/datasets/"

HASSBRAIN_PATH_TO_RT_MAIN = "/home/hassbrain_rest/rt_node_main.py"

MEDIA_ROOT = '/home/media/'

FILE_PATH_FIELD_DIRECTORY = "asdf"
MODEL_PATH_FIELD_DIRECTORY = "asdf"
