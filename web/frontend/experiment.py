from backend.models import *
from frontend.services import PollService
from frontend.util import get_server, input_is_empty
import pandas as pd
import logging
from pyadlml.constants import DEVICE, TIME, VALUE, ACTIVITY
from hass_api.rest import HARest
logger = logging.getLogger(__name__)


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

    srv = get_server()

    # 1. create dataset
    dataset_folder = settings.DATASET_PATH + ds_name +'/'
    ds = Dataset(name=ds_name,
                start_time=None,
                path_to_folder=dataset_folder,
                num_devices=len(Device.objects.all()),
                num_recorded_events=0,
                data_size=0
    )
    ds.save()

    # 2. create folders and inital files
    ds.setup_experiment_folder()


    # 3. Save room assignments
    ds.create_dev2room_assignment()
    ds.create_act2room_assignment()


    # TODO save prior information about persons

    # 3. mark all smartphone dirty and delete existing activity files
    for person in Person.objects.all():
        person.reset_activity_file()
        person.reset_smartphone()
        person.save()

    # 4. start logging service that polls data from home assistant
    PollService(srv).start()

    # 5. Repopulate all input_selects for hatrackers, turn of input_booleans
    #    for recording initialize activity file
    for person in Person.objects.all():
        if hasattr(person, 'hatracker'):
            person.hatracker.populate_input_selects()
            person.hatracker.reset_activity_df()
            person.hatracker.turn_off_input_boolean()

    # 6. If everything went well assign server the experiment
    ds.start_time = srv.get_current_time()
    ds.save()
    srv.dataset = ds
    srv.save()

    return True

def pause():
    """ indicates to pause logging on AA level and send a message to
        the HASS component to stop the webhook sendings
    """
    ds = get_server().dataset
    ds.logging = False
    ds.save()
    PollService(srv).stop()

def resume():
    ds = get_server().dataset
    ds.logging = True
    ds.save()
    PollService(srv).start()

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
    ds.end_time = srv.get_current_time()
    ds.save()

    # Create activity files from ha trackers and save to persons activity file
    for person in Person.objects.all():
        if hasattr(person, 'hatracker'):
            person.hatracker.transform_activity_df()


    # TODO Create activities from pause and resume experiment and add to all activity files



    # Substitute activity with mapping
    mapping = pd.read_csv(ds.get_activity_map_fp())
    mapping = {v: k for k, v  in mapping.set_index('id').to_dict()['activity'].items()}

    for person in Person.objects.all():
        person.remap_activity_file(mapping)

    # copy stuff activity files persons to dataset folder
    ds.copy_actfiles2dataset()



    PollService(srv).stop()

