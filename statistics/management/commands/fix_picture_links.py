from django.core.management.base import BaseCommand, CommandError
from statistics.models import Session

class Command(BaseCommand):
    def handle(self, *args, **options):
        sessions = Session.objects.all()

        for session in sessions:
            img_path = str(session.picture)
            if img_path.startswith('pictures/'):
                new_path = img_path.replace('pictures/', 'session_pictures/')
                self.stdout.write(new_path)
                session.picture = new_path
                session.save()
