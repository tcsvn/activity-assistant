#!/usr/bin/env python3

""" Example of resolving a service with a known name """

import logging
import sys

from zeroconf import Zeroconf

TYPE = '_http._tcp.local.'
NAME = '_activity_assist'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    zeroconf = Zeroconf()

    try:
        tmp = zeroconf.get_service_info(TYPE, NAME + '.' + TYPE)
        print('port: ', tmp.port)
        print('server: ', tmp.server)
        props = {}
        for key, value in tmp.properties.items():
            props[key.decode("utf-8")] = value.decode("utf-8")
        print(props)
    finally:
        zeroconf.close()