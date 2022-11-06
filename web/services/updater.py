


def scan_str2seconds(s):
    time = s[-1:]
    count = int(s[:-1])
    if time == 's':
        return count
    elif time == 'm':
        return count*60
    elif time == 'h':
        return count*3600




def start_updater_service():
    srv = get_server()
    # create url
    if settings.DEBUG:
        hostname = '709d7dbe-act-assist-dev'
    else:
        hostname = '709d7dbe-act-assist'
    url = 'http://' + hostname + ':8000/webhook'

    # create scanseconds
    secs = scan_str2seconds(srv.poll_interval)

    command = ["python3", settings.UPDATER_SERVICE_PATH,
        '--url', url,
        '--poll_interval', str(secs)
    ]
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    srv.poll_service_pid = proc.pid
    srv.is_polling = True
    srv.save()

def stop_updater_service():

    srv = get_server()
    if srv.is_polling:
        pid = srv.poll_service_pid
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            print('process allready deleted')
        srv.poll_service_pid = None
        srv.is_polling = False
        srv.save()