from backend.models import *
import pandas as pd
from pyadlml.dataset import DEVICE, TIME, VAL
from django.utils.timezone import now
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def get_device_names():
    res = []
    for dev in Device.objects.all():
        res.append(dev.name)
    return res

def get_activity_names():
    res = []
    for act in Activity.objects.all():
        res.append(act.name)
    return res
def get_person_names():
    aa_users = []
    for u in Person.objects.all():
        aa_users.append(u.name)
    return aa_users

def get_server():
    return Server.objects.get(id=1)

def getCountAssignedDevices(self):
    device_list = Device.objects.all()
    if device_list == []:
        return 0
    counter = 0
    for device in device_list:
        if device.location != None:
            counter += 1
    return counter

def scan_str2seconds(s):
    time = s[-1:]
    count = int(s[:-1])
    if time == 's':
        return count
    elif time == 'm':
        return count*60
    elif time == 'h':
        return count*3600

def start_updater_service():
    from subprocess import Popen, PIPE
    srv = get_server()
    # create url
    if settings.DEBUG:
        hostname = '709d7dbe-act-assist-dev'
    else:
        hostname = '709d7dbe-act-assist'
    url = 'http://' + hostname + ':8000/webhook'

    # create scanseconds
    secs = scan_str2seconds(srv.poll_interval)

    command = ["python3", settings.UPDATER_SERVICE_PATH,
        '--url', url,
        '--poll_interval', str(secs)
    ]
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    srv.poll_service_pid = proc.pid
    srv.is_polling = True
    srv.save()

def stop_updater_service():
    import os
    import signal
    srv = get_server()
    if srv.is_polling:
        pid = srv.poll_service_pid
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print('process allready deleted')
        srv.poll_service_pid = None
        srv.is_polling = False
        srv.save()


def start_zero_conf_server():
    """ starts a zero conf server and saves the pid in 
        the server zero_conf_pid field
    """
    import subprocess
    srv = get_server()
    if srv.zero_conf_pid is not None:
        stop_zero_conf_server()
    command = ["python3", settings.ZERO_CONF_MAIN_PATH]
    command.append('--hostname')
    if settings.DEBUG:
        command.append('709d7dbe-act-assist-dev')
    else:
        command.append('709d7dbe-act-assist')
    command += [
        '--api_path', '/api/v1', 
        '--webhook', '/webhook',
        '--port', str(8000)
    ]

    proc = subprocess.Popen(command, close_fds=True)
    srv.zero_conf_pid = proc.pid
    srv.save()

def stop_zero_conf_server():
    """ stops a zero conf server and clears the servers 
        zero_conf_pid field
    """
    import os
    import signal
    srv = get_server()
    if srv.zero_conf_pid is not None:
        pid = srv.zero_conf_pid
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print('process allready deleted')
        srv.zero_conf_pid = None
        srv.save()

import pandas as pd

def collect_data_from_hass():
    # this is the case where the data is pulled
    srv = get_server()
    ds = srv.dataset
    import frontend.experiment as experiment
    df_new = experiment.hass_db_2_data(settings.DB_URL, get_device_names())\
                .drop_duplicates()

    df_cur = experiment.load_data_file(ds.path_to_folder)

    df = pd.concat([df_cur, df_new], ignore_index=True)

    # save df
    dev_map = experiment.load_device_mapping(ds.path_to_folder, as_dict=True)
    df[DEVICE] = df[DEVICE].map(dev_map)
    df = df.drop_duplicates()
    df.to_csv(ds.path_to_folder + 'devices.csv', sep=',', index=False)


def get_line_numbers_file(file_path):
    with open(file_path) as my_file:
        return sum(1 for _ in my_file)

def get_folder_size(file_path):
    from pathlib import Path
    try:
        return Path(file_path).stat().st_size
    except:
        return 0