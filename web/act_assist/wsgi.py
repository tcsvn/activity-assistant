"""
WSGI config for activity-assistant project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
"""


from django.core.wsgi import get_wsgi_application

# TODO delete
import os
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'act_assist.settings')

application = get_wsgi_application()
