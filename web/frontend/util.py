from backend.models import *

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
def get_person_names():
    aa_users = []
    for u in Person.objects.all():
        aa_users.append(u.name)
    return aa_users

def get_server():
    return Server.objects.get(id=1)