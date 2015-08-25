import datetime

from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser, User

from views.public_views import home
from .models import Session

# Create your tests here.

def create_session(timedelta=0, duration=10, statistics_type="JF", is_visible=True, name="Leipzig 2015", description="80th International Session of the European Youth Parliament", picture="https://upload.wikimedia.org/wikipedia/commons/c/c4/PM5544_with_non-PAL_signals.png", email="test@example.com", country="DE", color="deep-orange", admin_user=None, submission_user=None):
    """
    This will create a session with the above specified data and defaults.
    """
    start_date = timezone.now() + datetime.timedelta(days=timedelta)
    end_date = timezone.now() + datetime.timedelta(days=timedelta + duration)

    return Session.objects.create(session_name=name, session_description=description, session_picture=picture, session_email=email, session_country=country, session_start_date=start_date, session_end_date=end_date, session_statistics=statistics_type, session_color=color, session_is_visible=is_visible, session_admin_user=None, session_submission_user=None)

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
