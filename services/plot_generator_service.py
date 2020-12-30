import argparse
import signal
import sys
import logging
import socket
from time import sleep
logger = logging.getLogger(__name__)
import logging

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    raise KeyboardInterrupt

def gen_plots_persons(dataset, data):
    from pyadlml.dataset.plot.activities import hist_counts, boxplot_duration, \
        hist_cum_duration, heatmap_transitions, ridge_line

    root_path = settings.MEDIA_ROOT + dataset.name + '/'
    for ps in dataset.person_statistics.all():
        sub_path = dataset.name + '/plots/' + ps.name + '/'
        path = settings.MEDIA_ROOT + sub_path
        df_activities = getattr(data, 'df_activities_{}'.format(ps.name))
        lst_acts = data.lst_activities

        try:
            hist_counts_filename = settings.PLOT_ACT_HIST_COUNTS_FN
            path_to_hist_counts = path + hist_counts_filename
            hist_counts(df_activities, lst_act=lst_acts, file_path=path_to_hist_counts)
            ps.plot_hist_counts = sub_path + hist_counts_filename
            logger.info('created hist_counts for ' + str(ps.name))
        except:
            logger.error("couldn't create histogram counts")

        try:
            boxplot_duration_filename = settings.PLOT_ACT_BP_DURATION_FN
            path_to_boxplot_duration = path + boxplot_duration_filename
            boxplot_duration(df_activities, lst_act=lst_acts, file_path=path_to_boxplot_duration)
            ps.plot_boxplot_duration = sub_path + boxplot_duration_filename
            logger.info('created boxplot_duration for ' + str(ps.name))
        except Exception as e:
            print(e)
            logger.error("couldn't create boxplot_duration")

        try:
            hist_cum_duration_filename = settings.PLOT_ACT_CUM_DUR_FN
            path_to_hist_cum_duration = path + hist_cum_duration_filename
            hist_cum_duration(df_activities, act_lst=lst_acts, file_path=path_to_hist_cum_duration)
            ps.plot_hist_cum_duration = sub_path + hist_cum_duration_filename
            logger.info('created hist_cum_duration for ' + str(ps.name))
        except:
            logger.error("couldn't create hist_cum_duration")
 
        try:
            heatmap_transitions_filename = settings.PLOT_ACT_HM_TRANS_FN
            path_to_heatmap_transitions = path + heatmap_transitions_filename
            heatmap_transitions(df_activities, lst_act=lst_acts, file_path=path_to_heatmap_transitions)
            ps.plot_heatmap_transitions = sub_path + heatmap_transitions_filename
            logger.info('created heatmap_transitions for ' + str(ps.name))
        except Exception as e:
            print(e)
            logger.error("couldn't create heatmap_transitions")

        try:
            ridge_line_filename = settings.PLOT_ACT_RIDGE_FN
            path_to_ridge_line = path + ridge_line_filename
            ridge_line(df_activities, lst_act=lst_acts, file_path=path_to_ridge_line)
            ps.plot_ridge_line = sub_path + ridge_line_filename
            logger.info('created ridge_line for ' + str(ps.name))
        except:
            logger.error("couldn't create ridge_line")

        ps.save()



def gen_plots_devices(dataset, data):
    from pyadlml.dataset.plot.devices import hist_trigger_time_diff, boxplot_on_duration, \
        heatmap_trigger_one_day, heatmap_trigger_time, heatmap_cross_correlation, \
        hist_on_off, hist_counts

    sub_path = dataset.name + '/plots/'
    path = settings.MEDIA_ROOT + sub_path

    try:
        hist_trigger_time_diff_filename = settings.PLOT_DEV_HIST_TRIG_TIME_FN
        path_to_hist_trigger_time_diff = path + hist_trigger_time_diff_filename
        hist_trigger_time_diff(data.df_devices, file_path=path_to_hist_trigger_time_diff)
        dataset.plot_hist_trigger_time_diff = sub_path + hist_trigger_time_diff_filename
        logger.info('created hist_trigger_time_diff')
    except:
        logger.error("couldn't create hist_trigger_time_diff")

    try:
        heatmap_trigger_time_filename = settings.PLOT_DEV_HM_TRIG_TIME_FN
        path_to_heatmap_trigger_time = path + heatmap_trigger_time_filename
        heatmap_trigger_time(data.df_devices, file_path=path_to_heatmap_trigger_time)
        dataset.plot_heatmap_trigger_time = sub_path + heatmap_trigger_time_filename
        logger.info('created heatmap_trigger_time')
    except:
        logger.error("couldn't create heatmap_trigger_time")


    try:
        heatmap_trigger_one_day_filename = settings.PLOT_DEV_HM_TRIG_ONE_DAY_FN
        path_to_heatmap_trigger_one_day = path + heatmap_trigger_one_day_filename
        heatmap_trigger_one_day(data.df_devices, file_path=path_to_heatmap_trigger_one_day)
        dataset.plot_heatmap_trigger_one_day = sub_path + heatmap_trigger_one_day_filename
        logger.info('created heatmap_trigger_one_day')
    except:
        logger.error("couldn't create heatmap_trigger_one_day")


    try:
        hist_counts_filename = settings.PLOT_DEV_HIST_COUNTS_FN
        path_to_hist_counts = path + hist_counts_filename
        hist_counts(data.df_devices, file_path=path_to_hist_counts)
        dataset.plot_hist_counts = sub_path + hist_counts_filename
        logger.info('created hist_counts')
    except:
        logger.error("couldn't create hist_counts")

    try:
        hist_counts_filename = settings.PLOT_DEV_HIST_ON_OFF_FN
        path_to_hist_counts = path + hist_counts_filename
        hist_on_off(data.df_devices, file_path=path_to_hist_counts)
        dataset.plot_hist_on_off = sub_path + hist_counts_filename
        logger.info('created hist_on_off')
    except:
        logger.error("couldn't create hist_on_off")

    try:
        hist_counts_filename = settings.PLOT_DEV_BP_ON_DUR_FN
        path_to_hist_counts = path + hist_counts_filename
        boxplot_on_duration(data.df_devices, file_path=path_to_hist_counts)
        dataset.plot_boxplot_on_duration = sub_path + hist_counts_filename
        logger.info('created boxplot_on_duration')
    except:
        logger.error("couldn't create boxplot_on_duration")

    try:
        hist_counts_filename = settings.PLOT_DEV_HM_CROSS_CORR_FN
        path_to_hist_counts = path + hist_counts_filename
        heatmap_cross_correlation(data.df_devices, file_path=path_to_hist_counts)
        dataset.plot_heatmap_cross_correlation = sub_path + hist_counts_filename
        logger.info('created heatmap_cross_correlation')
    except:
        logger.error("couldn't create heatmap_cross_correlation")

    dataset.save()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, terminateProcess)
    parser = argparse.ArgumentParser(description='run discovery')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--dataset-id', type=int, required=True)
    args = parser.parse_args()

    import os
    if args.debug:
        logger.info('running in debug mode')
        sys.path.append('/share/web')
        sys.path.append('/share/web/act_assist')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'act_assist.settings')
    else:
        logger.info('running in production mode')
        sys.path.append('/opt/activity_assistant/web')
        sys.path.append('/etc/opt/activity_assistant/')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    import django
    django.setup()

    from backend.models import Dataset
    import settings
    from frontend.util import get_person_names, get_server
    from pyadlml.dataset import load_act_assist

    try:          
        logger.info('loading dataset...')
        dataset = Dataset.objects.get(id=args.dataset_id)
        data = load_act_assist(dataset.path_to_folder, get_person_names())
        logger.info('generating plots for persons...')
        gen_plots_persons(dataset, data)
        logger.info('generating plots for devices...')
        gen_plots_devices(dataset, data)
    except KeyboardInterrupt:
        pass
    finally:
        logger.info('wrapping up service...')
        srv = get_server()
        srv.plot_gen_service_pid = None
        srv.save()
        logger.info('exited')