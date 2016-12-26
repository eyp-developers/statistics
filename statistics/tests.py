import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser, User

from views.public_views import home
from .models import Session, Committee

# Used for the image generation in create_test_image()
from io import BytesIO
from PIL import Image

# Create your tests here.

# Here we define some placeholder text we can use throughout the tests.

# 1 Paragraph long Lorem Ipsum
ips_1_p = "Emerging economies: The EUs joint free trade deal with multiple African countries has received both criticism and acclaim. How should the EU benefit from mutual trade and political cooperation whilst ensuring the development of human rights and enhancing environmental protection in the region?"
lor_1_p = "No mans land: Technologies with the potential to revolutionise transport, such as driverless cars and drone deliveries, will soon be ready to enter the commercial market. Balancing both the risks of introducing these technologies too early with their possible economic benefits, how should the EU position itself when legislating the introduction of these innovations?"

def create_test_image():
    """
    We need to generate an image to use for creating a session. This will generate such images.
    Code from: http://wildfish.com/blog/2014/02/27/generating-in-memory-image-for-tests-python/
    """
        file = BytesIO()
        image = Image.new('RGBA', size=(50, 50), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

def create_session(name="Leipzig 2015", description="80th International Session of the European Youth Parliament", email="test@example.com", country="DE", color="deep-orange", admin_user=None, submission_user=None, timedelta=0, duration=10, statistics_type="JF", is_visible=True):
    """
    This will create a session with the above specified data and defaults.
    """
    start_date = timezone.now() + datetime.timedelta(days=timedelta)
    end_date = timezone.now() + datetime.timedelta(days=timedelta + duration)

    # Here, we use create_test_image() to generate an image to use in our testing procedure
    picture = unicode(create_test_image().read(), errors='ignore')

    return Session.objects.create(session_name=name, session_description=description, session_picture=picture, session_email=email, session_country=country, session_start_date=start_date, session_end_date=end_date, session_statistics=statistics_type, session_color=color, session_is_visible=is_visible, session_admin_user=None, session_submission_user=None)

def create_committee(session, name="ENVI", topic=ips_1_p):
    """
    This will create a committee in the provided session.
    """
    return Committee.objects.create(session=session, committee_name=name, committee_topic=topic)

def create_user_max():
    """
    This will always create the example user max.
    """
    return User.objects.create_user(
        username='max', email='max@mustermann.de', password='top_secret')

class HomeViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()

    def test_home_view__without_any_sessions_created(self):
        """
        If no sessions exist the appropriate message should be shown.
        """
        response = self.client.get(reverse("statistics:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What's going on in GA?")
        self.assertContains(response, "No sessions are available.")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [])

    def test_home_view_with_one_session_created(self):
        """
        This test will create a session with all the standard values and see whether it shows up properly
        """
        create_session()
        response = self.client.get(reverse("statistics:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], ["<Session: Leipzig 2015>"])

    def test_home_view_with_two_sessions_created(self):
        """
        This test will create two sessions with all the standard values and see whether they shows up properly
        """
        create_session() #Creating Session 1
        create_session(name="Hiber 2015", description="4th International Forum of EYP Spain") #Creating Session 2
        response = self.client.get(reverse("statistics:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "Hiber 2015")
        self.assertContains(response, "4th International Forum of EYP Spain")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], ["<Session: Hiber 2015>", "<Session: Leipzig 2015>"])

    def test_home_view_with_one_non_public_session_created(self):
        """
        This test will create one non public session and test whether it does not show up and shows the proper message instead.
        """
        create_session(is_visible=False) #Creating Session 1
        response = self.client.get(reverse("statistics:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What's going on in GA?")
        self.assertContains(response, "No sessions are available.")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [])

    def test_home_view_with_one_public_and_one_non_public_session_created(self):
        """
        This test will create one public and one non public session and test whether they show up and do not show up as expected.
        """
        create_session(is_visible=False) #Creating non public Session 1
        create_session() # Creating public Session 1
        response = self.client.get(reverse("statistics:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What's going on in GA?")
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [ "<Session: Leipzig 2015>"])


class SessionViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()
        self.session = create_session()

    def test_session_view_with_all_standard_values(self):
        """
        This test makes sure an empty (no committees) session will be shown correctly.
        """
        response = self.client.get(reverse("statistics:session", args = [self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "No committees are available yet!")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")

    def test_session_view_with_one_committee(self):
        """
        This test makes sure that a session with one committee will properly display it.
        """
        committee = create_committee(session=self.session)
        response = self.client.get(reverse("statistics:session", args = [self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "ENVI")
        self.assertContains(response, ips_1_p)
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")

    def test_session_view_with_two_committees(self):
        """
        This test will make sure that a session with two committees will properly display them.
        """
        committee = create_committee(session=self.session)
        committee2 = create_committee(session=self.session, name="AFCO", topic=lor_1_p)
        response = self.client.get(reverse("statistics:session", args = [self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "ENVI")
        self.assertContains(response, ips_1_p)
        self.assertContains(response, "AFCO")
        self.assertContains(response, lor_1_p)
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")


class DebateViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()
        self.session = create_session()
        self.committee = create_committee(session=self.session)


    def test_debate_view_with_no_points(self):
        response = self.client.get(reverse("statistics:debate", args = [self.session.pk, self.committee.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debate: ENVI")
        self.assertContains(response, ips_1_p)
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()

    def test_login_view_loads_properly(self):
        """
        This test will see whether the login view contains the necessary elements needed to log in a user.
        """
        response = self.client.get(reverse("statistics:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
