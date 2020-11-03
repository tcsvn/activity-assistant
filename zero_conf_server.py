import argparse
import signal
import sys
import logging
import socket
from zeroconf import IPVersion, Zeroconf, ServiceInfo
from time import sleep

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    raise KeyboardInterrupt

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGTERM, terminateProcess)
    parser = argparse.ArgumentParser(description='run discovery')
    parser.add_argument('--port', type=int, required=True)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--hostname', type=str)
    parser.add_argument('--api_path', type=str)
    parser.add_argument('--webhook', type=str)
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)
    
    api_path = args.api_path
    hostname = args.hostname
    webhook = args.webhook
    port = args.port

    props={}
    if webhook is not None:
        props["webhook"] = webhook
    if api_path is not None:
        props['api_path'] = api_path 
    if hostname is not None:
        props['hostname'] = hostname
        
    info = ServiceInfo(
            "_http._tcp.local.",
            "_activity_assist._http._tcp.local.",
            port=port,
            properties=props,
            addresses=[socket.inet_aton("127.0.0.1")],
            server="ash-2.local.",
    )
    print("Registration of a service, press Ctrl-C to exit...")
    ip_version = IPVersion.V4Only
    zc = Zeroconf(ip_version=ip_version)
    zc.register_service(info)    
    
    try:
        while True:
            sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zc.unregister_service(info)
        zc.close()