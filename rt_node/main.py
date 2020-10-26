import argparse
import asyncio
import sys
import traceback
from hassbrain_rt_node.controller import Controller

HB_ADDR = "http://134.2.56.118:8000"
HB_USER = "admin"
HB_PW = "asdf"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='run logger for data')
    parser.add_argument('--host', dest='server_address',
                        help='address of hassbrain webserver')
    parser.add_argument('-u', dest='user_name',
                        help='name of user to authenticate against hassbrain')
    parser.add_argument('-p', dest='password',
                        help='password of user to authenticate against hassbrain')
    args = vars(parser.parse_args())
    server_address = args['server_address']
    user_name = args['user_name']
    password = args['password']

    # start asynchrounous event loop
    #ctrl = Controller(HB_ADDR, HB_USER, HB_PW)
    ctrl = Controller(server_address, user_name, password)
    ctrl.run()

