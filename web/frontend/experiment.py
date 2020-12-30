from backend.models import *
import os
import signal
from pathlib import Path
from frontend.util import get_server, get_device_names, start_updater_service, \
    stop_updater_service, get_current_time, get_activity_names, input_is_empty
import pandas as pd
import logging
from pyadlml.dataset._datasets.activity_assistant import _read_devices
from pyadlml.dataset import DEVICE, TIME, VAL, ACTIVITY

# Get an instance of a logger
logger = logging.getLogger(__name__)

def is_active():
    srv = get_server()
    return not srv.dataset is None

def get_status():
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
    return _read_devices(
        path_to_folder + settings.DATA_FILE_NAME,
        path_to_folder + settings.DATA_MAPPING_FILE_NAME
    )

def create_data_file(path_to_folder):
    """ creates inital device file 
    Example
        time,device,val
    """
    fp = path_to_folder + settings.DATA_FILE_NAME
    pd.DataFrame(columns=[TIME, DEVICE, VAL])\
        .to_csv(fp, sep=',', index=False)

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

def create_activity_mapping_file(path_to_folder):
    """ creates an activity mapping file with the current selected activities
        for logging. 

    Example
        id,activities
        0,eat
        1,sleep
    """
    file_path = path_to_folder + settings.ACTIVITY_MAPPING_FILE_NAME
    df = pd.DataFrame(data=get_activity_names(), columns=[ACTIVITY])
    df.to_csv(file_path, sep=',', index_label='id')

def load_device_mapping(path_to_folder, as_dict=False):
    fp = path_to_folder + settings.DATA_MAPPING_FILE_NAME
    if as_dict:
        return pd.read_csv(fp, index_col=DEVICE).to_dict()['id']
    else:
        return pd.read_csv(fp, index_col='id').to_dict()[DEVICE]


def start(request):
    """ creates a new dataset object and assigns it to the server
        that it knows an experiment is running. Also creates folders
        like 
            /data/datasets/<datasetname>/activities_subject_<person>.csv>
            /data/datasets/<datasetname>/devices.csv
            /data/datasets/<datasetname>/device_mapping.csv
            ...
        
    Parameters
    ----------
    request : 

    Returns
    -------
        True if it was successfull
    """
    ds_name = request.POST.get("name","").strip()
    try:
        if input_is_empty(ds_name):
            return False
        Dataset.objects.get(name=ds_name)
        return False
    except:
        pass

    # 1. create dataset 
    dataset_folder = settings.DATASET_PATH + ds_name +'/'
    ds = Dataset(name=ds_name, 
                start_time=get_current_time(), 
                path_to_folder=dataset_folder,
                num_devices=len(Device.objects.all()),
                num_recorded_events=0,
                data_size=0
    )
    ds.save()
    # 
    srv = get_server()
    srv.dataset = ds
    srv.save()

    # 2. create folders and inital files
    Path(ds.path_to_folder).mkdir(mode=0o777, parents=True, exist_ok=False)
    create_data_file(ds.path_to_folder)
    create_device_mapping_file(ds.path_to_folder)
    create_activity_mapping_file(ds.path_to_folder)

    # TODO save prior information about persons
    # TODO save room assignments of sensors and activities

    # 3. mark all smartphone dirty and delete existing activity files
    for person in Person.objects.all():
        person.reset_activity_file()
        if hasattr(person, 'smartphone') and person.smartphone is not None:
            person.smartphone.synchronized = False
            person.smartphone.save()
        
        # create new personstatistic
        ps = PersonStatistic(name=person.name, 
                            dataset=ds,
                            num_activities=len(Activity.objects.all()),
                            num_recorded_activities=0
        )
        person.person_statistic = ps
        person.person_statistic.save()
        person.save()
        
    # 4. start logging service that polls data from home assistant
    start_updater_service()
    return True

def pause():
    """ indicates to pause logging on AA level and send a message to 
        the HASS component to stop the webhook sendings
    """
    ds = get_server().dataset
    ds.logging = False
    ds.save()
    stop_updater_service()

def resume():
    ds = get_server().dataset
    ds.logging = True
    ds.save()   
    start_updater_service()

def finish():
    # get one last pull from homeassistant
    from frontend.util import collect_data_from_hass
    collect_data_from_hass()

    # deassociate dataset
    srv = get_server()
    ds = srv.dataset
    srv.dataset = None
    srv.save()

    # wrap up dataset
    ds.logging = False
    ds.end_time = get_current_time()
    ds.save()

    # dissacosiate person statistics from persons
    for person in Person.objects.all():
        person.person_statistic = None
        person.save()

    # copy stuff activity files persons to dataset folder
    copy_actfiles2dataset(ds)

    stop_updater_service()


def copy_actfiles2dataset(ds):
    import shutil
    for person in Person.objects.all():
        src = settings.MEDIA_ROOT + person.activity_file.name
        dest = ds.path_to_folder + settings.ACTIVITY_FILE_NAME%(person.name)
        shutil.copyfile(src, dest) 
