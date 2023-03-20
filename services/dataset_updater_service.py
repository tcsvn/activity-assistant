import argparse
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from frontend.util import collect_data_from_hass
import signal
import sys
import logging
import socket
from time import sleep
from datetime import timedelta
"""
This is just a simple server that makes a get request on the home assistant webhook

"""

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    raise KeyboardInterrupt

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGTERM, terminateProcess)
    parser = argparse.ArgumentParser(description='run discovery')
    parser.add_argument('--url', type=str, required=True)
    parser.add_argument('--poll_interval', type=int, required=True)
    args = parser.parse_args()

    url = args.url
    poll_int = args.poll_interval

    print("Registration of a service, press Ctrl-C to exit...")
    try:
        while True:
           try:
               print('start collection....')
               collect_data_from_hass()
               print('end collection....')
           except Exception as e:
               print(e)
           print('start sleeping...')
           sleep(poll_int)
    except KeyboardInterrupt:
        pass
