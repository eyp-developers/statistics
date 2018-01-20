from statistics.models import Session

sessions = Session.objects.all()

for session in sessions:
    img_path = str(session.picture)
    if img_path.startswith('pictures/'):
        new_path = img_path.replace('pictures/', 'session_pictures/')
        print(new_path)
        session.picture = new_path
        session.save()
