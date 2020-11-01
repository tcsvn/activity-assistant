from backend.models import *
import pandas as pd

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
    elif srv.dataset.logging:
        return 'running'
    else:
        return 'paused'

def load_activity_file(dataset, person):
    raise NotImplementedError

def load_data_file(dataset):
    raise NotImplementedError

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
    df = pd.DataFrame(data=get_device_names(), columns=['device'])
    df.to_csv(file_path, sep=',', index_label='id') 