from django.db import models
import shutil
from pygments.lexers import get_all_lexers
from pyadlml.constants import TIME, DEVICE, VALUE, START_TIME, END_TIME, ACTIVITY
import pandas as pd
from pygments.styles import get_all_styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import os
import logging
from pathlib import Path
import pathlib
from django.core.files import File
from django.http import FileResponse
from backend.util import create_zip
from hass_api.rest import HARest

from pyadlml.dataset.act_assist import read_devices, write_devices, write_activities

def hatracker_fp(instance, filename):
    # file will be uploaded to MEDIA_ROOT/activities_subject_<person.name>.csv
    return 'ha_tracker_' + instance.person.name + '_' + instance.ACTIVITY_FN
   


class HATracker(models.Model):
    from .models import Person, Activity, OverwriteStorage
    person = models.OneToOneField(Person, null=True, blank=True, on_delete=models.CASCADE)
    logging = models.BooleanField(default=False)
    logged_activity = models.ForeignKey(Activity, null=True, 
            on_delete=models.SET_NULL, related_name='%(class)s_logged')
 
    # Names of the corresponding Home Assistant components
    input_select = models.CharField(max_length=20)
    input_boolean = models.CharField(max_length=20)

    # A file containing a dataframe (time, device, value) that stores the 
    # input selects and input_booleans for the time of an experiment and is 
    # later transformed into a persons activity file 
    activity_file = models.FileField(null=True, upload_to=hatracker_fp, storage=OverwriteStorage())
    ACTIVITY_FN = 'activities.csv'

    def save(self, *args, **kwargs):
        # create additional user with one to one relationship so that
        # one device can't alter the anything but its own person
        #User.objects.create_user(username=self.name, email='test@test.de', password='test')
        super(HATracker, self).save(*args, **kwargs)

        try:
            self.activity_file.path
        except ValueError:
            self.reset_activity_df()
 

    def reset_activity_df(self) -> None:
        """ Deletes activity file and creates new empty dataframe
        """
        from pyadlml.constants import TIME, DEVICE, VALUE
        fp = Path(hatracker_fp(self, ''))
        fp.parent.mkdir(parents=True, exist_ok=True)
        #fp = 'ha_tracker_admin/activities.csv'
        self.activity_file.delete()

        df_empty = pd.DataFrame(columns=[TIME, DEVICE, VALUE])
        write_activities(df_empty, fp)

        self.activity_file = File(open(fp))
        self.save()

    
    def update_activity_df(self, df: pd.DataFrame) -> None:
        """ Append new activity recordings to existing activity dataframe
        """
        fp = self.activity_file.path

        df_hat = read_devices(fp)
        df = pd.concat([df_hat, df]).drop_duplicates()
        write_devices(df, fp)

    def populate_input_selects(self) -> None:
        """ Set the input selects to the given activities
        """
        from .models import Activity
        act_list = Activity.get_all_names()
        HARest().populate_input_selects(self.input_select, act_list)

    def turn_off_input_boolean(self):
        """ Turns of the input selected boolean at homeassistant
        """
        HARest().turn_off_input_boolean(self.input_boolean)


    def inputxs_exist_at_ha(self):
        har = HARest()
        return har.device_exists(self.input_boolean) \
           and har.device_exists(self.input_select)

    def fetch_logging_fromHA(self):
        return ('on' == HARest().get_state(self.input_boolean))

    def fetch_activity_fromHA(self):
        from .models import Activity
        sel_activity = HARest().get_state(self.input_select)
        activity = Activity.objects.get(name=sel_activity)
        return activity

    def update_attributes(self):
        """ Calls the home assistant api and checks if the device is logging
        """
        self.logging = self.fetch_logging_fromHA()
        self.logged_activity = self.fetch_activity_fromHA()


    def transform_activity_df(self):
        """ From input_select/boolean recordings [TIME, DEVICE, VAL]
            create an activity dataframe [START_TIME, END_TIME, ACTIVITY]
        """
        out_path = self.person.activity_file.path
        
        df = read_devices(self.activity_file.path)\
               .drop_duplicates()\
               .sort_values(by=TIME)

        # Do nothing if not anything is recorded
        if df.empty:
            return

        # Split into input_select and input_boolean 
        mask_rec_device = (df[VALUE] == True) | (df[VALUE] == False)
        df_recs = df[mask_rec_device].copy().reset_index(drop=True)
        df_recs[VALUE] = df_recs[VALUE].astype(bool)
        df = df[~mask_rec_device].copy().reset_index(drop=True)
        
        # Remove all non valid activities (if user added categories to helper on HA after 
        #                                  experiment creation)
        from .models import Activity
        from pyadlml.dataset._core.devices import correct_on_off_inconsistency
        from pyadlml.dataset._core.activities import create_empty_activity_df

        df = df[df[VALUE].isin(Activity.get_all_names())]

        df = df.rename(columns={TIME: START_TIME, VALUE: ACTIVITY})
        df[END_TIME] = df[START_TIME].shift(-1)
        df = df.drop(columns=[DEVICE])
        df = df[[START_TIME, END_TIME, ACTIVITY]]

        # Create start_time, end_time tuples and start with first true value
        # otherwise the tuples ordering is wrong
        df_recs = df_recs.loc[df_recs[VALUE].idxmax():df_recs[VALUE].where(~df_recs[VALUE]).last_valid_index()]
        df_recs = correct_on_off_inconsistency(df_recs)
        tmp = zip(df_recs.loc[df_recs[VALUE] == True, TIME].values,
                  df_recs.loc[df_recs[VALUE] == False, TIME].values)

        # End last activity (NaT) a bit later then the last device event
        df.at[df.index[-1], END_TIME] = str(pd.Timestamp(df_recs[TIME].iloc[-1]) + pd.Timedelta('1s'))

        df_acts = create_empty_activity_df()

        for st, et in tmp:
            # Get activity ending inside and overlapping start time
            tmp1 = df[(df[START_TIME] < st) & (st < df[END_TIME]) & (df[END_TIME] < et)].reset_index()

            # Get activities between 
            tmp2 = df[(st < df[START_TIME]) & (df[END_TIME] < et)]

            # Get activity starting inside and overlapping end_time
            tmp3 = df[(st < df[START_TIME]) & (df[START_TIME] < et) & (et < df[END_TIME])].reset_index()

            # Get activity overlapping total area
            tmp4 = df[(df[START_TIME] < st) & (et < df[END_TIME])].reset_index()

            def act_append(df_old, st, et, act):
                return pd.concat([df_old, pd.Series({START_TIME:st, END_TIME:et, ACTIVITY:act}).to_frame().T])

            df_acts = pd.concat([df_acts, tmp2])
            if not tmp1.empty:
                df_acts = act_append(df_acts, st, tmp1.loc[0,END_TIME], tmp1.loc[0, ACTIVITY])
            if not tmp3.empty:
                df_acts = act_append(df_acts, tmp3.loc[0, START_TIME], et, tmp3.loc[0, ACTIVITY])
            if not tmp4.empty: 
                df_acts = act_append(df_acts, st, et, tmp4.loc[0, ACTIVITY])

        df_acts = df_acts.reset_index(drop=True)\
                         .sort_values(by=START_TIME)

        write_activities(df_acts, out_path) 

