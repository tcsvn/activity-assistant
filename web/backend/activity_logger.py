import datetime
import csv
TIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'

def delete_last_row(file_path):
    with open(file_path,'r') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        rows = list(filereader)

    with open(file_path, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for i, row in enumerate(rows):
            if i == len(rows)-1:
                break
            filewriter.writerow(row)

def get_last_row(file_path):
    with open(file_path,'r') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        rows = list(filereader)
        last_row = rows[-1:]
        last_row =  last_row[0]
        return last_row

def append_last_row(file_path, row):
    with open(file_path, 'a') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(row)


def create_new_act_entry(file_path, activity):
    """
    :param file_path:
    :param activity:
    :return:
    """
    time_stamp = datetime.datetime.now().strftime(TIME_FORMAT)
    append_last_row(file_path, [time_stamp, activity])


def finish_existing_act_entry(file_path, activity):
    """

    :param file_path:
    :param activity:
    :return:
    """
    time_end_stamp = datetime.datetime.now().strftime(TIME_FORMAT)
    last_row = get_last_row(file_path)
    time_begin_stamp = last_row[0]

    assert len(last_row) == 2
    assert activity == last_row[1]
    delete_last_row(file_path)
    append_last_row(file_path, [time_begin_stamp, time_end_stamp, activity])

