"""
WSGI config for eypstats project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling


application = Cling(MediaCling(get_wsgi_application()))

# application = get_wsgi_application()
