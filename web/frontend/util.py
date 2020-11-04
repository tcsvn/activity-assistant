from backend.models import *
import pandas as pd
from pyadlml.dataset import DEVICE, TIME, VAL

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

def is_experiment_active():
    srv = get_server()
    return not srv.dataset is None

def get_experiment_status():
    """ gets the experiment status of the server 
    """
    srv = get_server()
    if srv.dataset is None:
        return 'not_running'
    elif srv.is_polling:
        return 'running'
    else:
        return 'paused'

def load_activity_file(dataset, person):
    raise NotImplementedError

def load_data_file(path_to_folder):
    from pyadlml.dataset._datasets.activity_assistant import _read_devices
    return _read_devices(
        path_to_folder + settings.DATA_FILE_NAME,
        path_to_folder + settings.DATA_MAPPING_FILE_NAME
    )

def create_data_file(path_to_folder):
    """ creates inital device file 
    Example
        time,device,val
    """
    from pyadlml.dataset import TIME, DEVICE, VAL
    fp = path_to_folder + settings.DATA_FILE_NAME
    pd.DataFrame(columns=[TIME, DEVICE, VAL])\
        .to_csv(fp, sep=',', index=False)

def create_activity_files(path_to_folder, person_list):
    """ creates inital activity file for every person in dataset folder
    Example
        start_time, end_time, activity

    """
    from pyadlml.dataset.activities import _create_activity_df

    for person in person_list:
        fp = path_to_folder + settings.ACTIVITY_FILE_NAME%(person.name)
        _create_activity_df().to_csv(fp, sep=',', index=False)


def create_device_mapping_file(path_to_folder):
    """ creates a device mapping file with the current devices selected
        for logging. 

    Example
        id,devices
        0,binary_sensor.ping_chris_laptop
        1,binary_sensor.ping_chris_pc
    """
    file_path = path_to_folder + settings.DATA_MAPPING_FILE_NAME 
    df = pd.DataFrame(data=get_device_names(), columns=[DEVICE])
    df.to_csv(file_path, sep=',', index_label='id') 


def load_device_mapping(path_to_folder, as_dict=False):
    fp = path_to_folder + settings.DATA_MAPPING_FILE_NAME
    if as_dict:
        return pd.read_csv(fp, index_col=DEVICE).to_dict()['id']
    else:
        return pd.read_csv(fp, index_col='id').to_dict()[DEVICE]


def hass_db_2_data(db_url, device_list):
    from pyadlml.dataset._datasets.homeassistant import hass_db_2_df

    df = hass_db_2_df(db_url)
    df = df[df['entity_id'].isin(device_list)]
    df[TIME] = pd.to_datetime(df['last_changed'])
    df[VAL] = (df['state'] == 'on').astype(int)
    df[DEVICE] = df['entity_id']
    df = df[[TIME, DEVICE, VAL ]]
    return df

def pause_experiment():
    """ indicates to pause logging on AA level and send a message to 
        the HASS component to stop the webhook sendings
    """
    ds = get_server().dataset
    ds.logging = False
    ds.save()
    stop_updater_service()

def continue_experiment():
    ds = get_server().dataset
    ds.logging = True
    ds.save()   
    start_updater_service()

def finish_experiment():
    srv = get_server()
    ds = srv.dataset
    srv.dataset = None
    srv.save()
    ds.logging = False
    from django.utils.timezone import now
    ds.end_time = now()
    ds.save()
    stop_updater_service()

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