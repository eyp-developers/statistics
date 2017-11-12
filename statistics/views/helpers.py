from raven import Client
from django.conf import settings

raven_client = Client(settings.RAVEN_CONFIG['dsn'])
