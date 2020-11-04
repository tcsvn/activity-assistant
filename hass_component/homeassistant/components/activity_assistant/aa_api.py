import aiohttp
from datetime import timedelta

class ActAssist:
    def __init__(self, session: aiohttp.ClientSession, host, port=8000, \
        webhook_url='/webhook', api_url='/api/v1')  -> None:
        self._session = session
        self.host = host
        self.port = port
        self.wh_url = 'http://' + host + ':' + str(port) + webhook_url
        self.api_url = 'http://' + host + ':' + str(port) + api_url

    async def call_webhook(self) -> None:
        """ calls the webhook
        """
        async with self._session.get(self.wh_url) as response:
            await response.text()
            return response.status


    async def get_scan_interval(self) -> int:
        """ returns timedelta object of scan interal
        """
        url = self.api_url + '/server/1/?format=json'
        async with self._session.get(url) as resp:
            json = await resp.json()
            s = json['poll_interval']
            time = s[-1:]
            count = int(s[:-1])
            if time == 's':
                return timedelta(seconds=count)
            elif time == 'm':
                return timedelta(minutes=count)
            elif time == 'h':
                return timedelta(hours=count)
            else:
                raise ValueError
