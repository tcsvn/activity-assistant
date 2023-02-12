import settings
from subprocess import Popen, PIPE
import os
import signal
import subprocess

class Service():
    ADDON_DEBUG_NAME = '709d7dbe-act-assist-dev'
    ADDON_PROD_NAME = '709d7dbe-act-assist'
    def __init__(self, srv, serv_loc):
        self.srv = srv
        self.serv_loc = serv_loc
        self.pid = None


    def is_running(self):
        """ Check For the existence of a unix pid. """
        if self.pid is None:
            return False

        try:
            os.kill(self.pid, 0)
        except OSError:
            return False
        else:
            return True

class PollService(Service):
    def __init__(self, srv): 
        super().__init__(srv=srv, serv_loc=settings.UPDATER_SERVICE_PATH)
        try:
            self.port = srv.get_address_port() 
        except AttributeError:
            self.port = None
        self.pid = self.srv.poll_service_pid


    def update_status(self):
        if not self.is_running():
            self.pid = None
            self.srv.poll_service_pid = None
            self.srv.save()

    def start(self):
        """
        """
        # Create url
        hostname = self.ADDON_DEBUG_NAME if settings.DEBUG else self.ADDON_PROD_NAME
        url = 'http://' + hostname + ':' + self.port + '/webhook'

        # create scanseconds
        from web.frontend.util import scan_str2seconds
        secs = scan_str2seconds(self.srv.poll_interval)

        command = ["python3", self.serv_loc,
            '--url', url,
            '--poll_interval', str(secs)
        ]


        proc = Popen(command, stdout=PIPE, stderr=PIPE)


        self.srv.poll_service_pid = proc.pid
        self.srv.is_polling = True
        self.srv.save()

    def stop(self):
        """
        """
        if self.srv.is_polling:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                print('process allready deleted')
            except TypeError:
                print('process allready deleted')
            self.pid = None
            self.srv.poll_service_pid = None
            self.srv.is_polling = False
            self.srv.save()




class ZeroConfService(Service):

    def __init__(self, srv):
        super().__init__(srv=srv, serv_loc=settings.ZERO_CONF_MAIN_PATH)
        self.srv = srv
        try:
            self.port = srv.get_address_port() 
        except AttributeError:
            self.port = None
        self.pid = self.srv.zero_conf_pid

    def update_status(self):
        if not self.is_running():
            self.pid = None
            self.srv.zero_conf_pid = None
            self.srv.save()

    def start(self):
        """ starts a zero conf server and saves the pid in
            the server zero_conf_pid field
        """
        if self.srv.zero_conf_pid is not None:
            self.stop()

        # Create command
        hostname = self.ADDON_DEBUG_NAME if settings.DEBUG else self.ADDON_PROD_NAME
        command = ["python3", self.serv_loc, 
            '--hostname', hostname,
            '--api_path', '/api/v1',
            '--webhook', '/webhook',
            '--port', str(self.port)
        ]

        proc = subprocess.Popen(command, close_fds=True)

        # Save pid to server
        self.srv.zero_conf_pid = proc.pid
        self.srv.save()

    def stop(self):
        """ Stops a zero conf server and clears the servers
            zero_conf_pid field
        """
        if self.pid is not None:
            try:
                os.kill(self.pid, signal.SIGTERM)
            except ProcessLookupError:
                print('process allready deleted')
            self.pid = None
            self.srv.zero_conf_pid = None
            self.srv.save()