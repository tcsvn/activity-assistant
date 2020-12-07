import sys
import os
from act_assist.settings import BASE_DIR

sys.path.append(os.path.realpath('.'))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

STATIC_ROOT = '/var/cache/activity_assistant/static/'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mawcf9#i&c3cl#g47-oks8wio8%7205@0u_g4233$q30pcgzdn'
#SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
DEBUG = os.getenv('DJANGO_DEBUG', False)


STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/static"),
    '/opt/activity_assistant/web/frontend/static',
]

ZERO_CONF_MAIN_PATH = "/opt/zero_conf_server.py"
UPDATER_SERVICE_PATH = "/opt/dataset_updater_service.py"