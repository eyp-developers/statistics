import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from PIL import Image
from io import StringIO

from ..models import Session, Committee

# 1 Paragraph long Lorem Ipsum
ips_1_p = "Emerging economies: The EUs joint free trade deal with multiple African countries has received both criticism and acclaim. How should the EU benefit from mutual trade and political cooperation whilst ensuring the development of human rights and enhancing environmental protection in the region?"
lor_1_p = "No mans land: Technologies with the potential to revolutionise transport, such as driverless cars and drone deliveries, will soon be ready to enter the commercial market. Balancing both the risks of introducing these technologies too early with their possible economic benefits, how should the EU position itself when legislating the introduction of these innovations?"

def create_test_image():
    image_file = StringIO()
    image = Image.new('RGBA', size=(100, 100), color=(0, 0, 0))
    image.save(image_file, 'png')
    image_file.seek(0)
    return ContentFile(image_file.read(), 'test.png')

def create_session(name="Leipzig 2015", description="80th International Session of the European Youth Parliament", email="test@example.com", country="DE", color="deep-orange", admin_user=None, submission_user=None, timedelta=0, duration=10, statistics_type="JF", is_visible=True):
    """
    This will create a session with the above specified data and defaults.
    """
    start_date = timezone.now() + datetime.timedelta(days=timedelta)
    end_date = timezone.now() + datetime.timedelta(days=timedelta + duration)

    # Here, we use create_test_image() to generate an image to use in our testing procedure
    picture = create_test_image()

    return Session.objects.create(name=name, description=description, picture=picture, email=email, country=country, start_date=start_date, end_date=end_date, session_statistics=statistics_type, is_visible=is_visible, admin_user=None, submission_user=None)

def create_committee(session, name="ENVI", topic=ips_1_p):
    """
    This will create a committee in the provided session.
    """
    return Committee.objects.create(session=session, name=name, topic=topic)

def create_user_max():
    """
    This will always create the example user max.
    """
    return User.objects.create_user(
        username='max', email='max@mustermann.de', password='top_secret')
