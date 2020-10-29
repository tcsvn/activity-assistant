from backend.models import *

def get_device_by_name():
    pass

def get_device_by_id(ide):
    return Device.objects.get(id=ide)

def get_device_names():
    res = []
    for dev in Device.objects.all():
        res.append(dev.name)
    return res

def get_activity_names():
    res = []
    for act in Activity.objects.all():
        res.append(act.name)
    return res

def get_server():
    return Server.objects.get(id=1)