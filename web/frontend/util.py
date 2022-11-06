from backend.models import *
import pandas as pd
from pyadlml.constants import DEVICE, TIME, VALUE
from django.utils.timezone import now
from pyadlml.dataset import load_homeassistant_devices
import logging
import sqlalchemy
from sqlalchemy import create_engine
import os
import pandas as pd
import pytz
from datetime import datetime
from pathlib import Path

# Get an instance of a logger
logger = logging.getLogger(__name__)


def input_is_empty(input):
    return input.strip() == ""


def get_server():
    return Server.objects.get(id=1)


def collect_data_from_hass():
    # this is the case where the data is pulled
    srv = get_server()
    ds = srv.dataset

    df_cur = ds.load_data_file()

    # use either the last timestamp from the dataframe or if it doesn't
    # exist the start timestamp of the dataset
    try:
        # Returns last_ts as UTC value
        last_ts =df_cur[TIME].values[-1]
    except IndexError:
        last_ts = ds.start_time

    # Home Assistant stores values in utc, therefore before querying convert the timestamps
    last_ts_utc = format_timestamp(localtime_to_utc(last_ts, srv.time_zone))
    now_ts_utc = format_timestamp(datetime.utcnow()) 

    device_lst = Device.get_all_names()

    # Add devices from the ha trackers
    ha_trackers = HATracker.objects.all()
    ha_dev_list = []
    for hat in ha_trackers:
        device_lst.extend([hat.input_boolean, hat.input_select])
        ha_dev_list.extend([hat.input_boolean, hat.input_select])

    df_new = load_homeassistant_devices(
        srv.hass_db_url,
        device_lst,
        last_ts_utc, now_ts_utc
    ).drop_duplicates()

    # Convert the utc timestamps back to the local time_zone 
    df_new[TIME] = pd.to_datetime(df_new[TIME].apply(utc_to_localtime, args=(srv.time_zone,)))

    # For every ha tracker collect timestamps
    hat_tracker_mask = df_new[DEVICE].isin(ha_dev_list)
    df_hatr = df_new[hat_tracker_mask]
    df_new = df_new[~hat_tracker_mask]
        
    for hatr in ha_trackers:
        df_hat_new = df_hatr[df_hatr[DEVICE].isin([hatr.input_boolean, hatr.input_select])]
        hatr.update_activity_df(df_hat_new)
    df = pd.concat([df_cur, df_new], ignore_index=True)

    # save df
    dev_map = ds.load_device_mapping(as_dict=True)
    df[DEVICE] = df[DEVICE].map(dev_map)
    df = df.drop_duplicates().sort_values(by=TIME, ascending=True)
    df.to_csv(ds.path_to_folder + 'devices.csv', sep=',', index=False)


def create_django_file(self, file_path, folder_name, file_name):
    from django.core.files.base import File
    django_file = File(open(file_path, "rb"))
    django_file.name = folder_name + "/" + file_name
    return django_file




def format_timestamp(ts):
    """ creates a timestamp in the format "YYYY-MM-DD HH:MM:SS:microseconds"
        eg. 2020-12-09 16:35:13.12904
    Returns
    -------
    current_time : str
    """
    if not isinstance(ts, pd.Timestamp):
        ts = pd.Timestamp(ts)
    if isinstance(ts, pd.Timestamp):
        return ts.strftime("%Y-%m-%d %H:%M:%S.%f")
    else:
        raise ValueError

def localtime_to_utc(ts, tzone):
    utcoffset = pd.Timestamp(ts, tz=tzone).tzinfo._utcoffset
    res = pd.Timestamp(ts) - utcoffset
    return format_timestamp(res)

def utc_to_localtime(ts, to_zone):
    """ ts time string
    """
    tmp = pd.Timestamp(ts,tz='UTC').astimezone(to_zone)
    return format_timestamp(tmp)


def get_line_numbers_file(file_path):
    with open(file_path) as my_file:
        return sum(1 for _ in my_file)

def get_folder_size(file_path):
    try:
        return Path(file_path).stat().st_size
    except:
        return 0



def ping_db(db_url):
    """ Creates a connection to a mysql database. Raises an error when failing.
        Is used to test the connectivity
    """

    engine = sqlalchemy.create_engine(db_url)
    with engine.connect() as connection:
        pass


def scan_str2seconds(s):
    time = s[-1:]
    count = int(s[:-1])
    if time == 's':
        return count
    elif time == 'm':
        return count*60
    elif time == 'h':
        return count*3600
