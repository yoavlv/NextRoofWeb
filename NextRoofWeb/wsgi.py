"""
WSGI config for NextRoofWeb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import site
from django.core.wsgi import get_wsgi_application

sys.path.append('C:/Users/yoavl/NextRoofWeb')

os.environ['DJANGO_SETTINGS_MODULE'] = 'NextRoofWeb.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NextRoofWeb.settings')

application = get_wsgi_application()

