import argparse
import sys
import logging
import socket
from zeroconf import IPVersion, Zeroconf, ServiceInfo
from time import sleep

def create_discovery_info(props):
    import socket
    info = ServiceInfo(
            "_http._tcp.local.",
            "_activity_assist._http._tcp.local.",
            port=8000,
            properties=props,
            addresses=[socket.inet_aton("127.0.0.1")],
            server="ash-2.local.",
    )
    return info


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='run discovery')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    props={
        "api_path":'/api/v1',
        "webhook_link":'/webhook'
    }
    info = create_discovery_info(props)
   
    print("Registration of a service, press Ctrl-C to exit...")
    ip_version = IPVersion.V4Only
    zc = Zeroconf(ip_version=ip_version)
    zc.register_service(info)    
    
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering...")
        zeroconf.unregister_service(info)
        zeroconf.close()