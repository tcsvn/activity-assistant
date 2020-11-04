import argparse
import signal
import sys
import logging
import socket
from time import sleep

import aiohttp
import asyncio
from datetime import timedelta

def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    raise KeyboardInterrupt

async def main(url, poll_int):
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url) as resp:
                tmp = await resp.text()
                await asyncio.sleep(poll_int)


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
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(main(url, poll_int))
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()