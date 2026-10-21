import datetime
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Point
from .helpers import create_session, create_committee, create_user_max


class HomeViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()

    def test_home_view__without_any_sessions_created(self):
        """
        If no sessions exist the appropriate message should be shown.
        """
        response = self.client.get(reverse("statisticscore:home"))
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
        session_leipzig = create_session()
        response = self.client.get(reverse("statisticscore:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [session_leipzig])

    def test_home_view_with_two_sessions_created(self):
        """
        This test will create two sessions with all the standard values and see whether they shows up properly
        """
        session_leipzig = create_session() #Creating Session 1
        session_hiber = create_session(name="Hiber 2015", description="4th International Forum of EYP Spain") #Creating Session 2
        response = self.client.get(reverse("statisticscore:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "Hiber 2015")
        self.assertContains(response, "4th International Forum of EYP Spain")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [session_hiber, session_leipzig])

    def test_home_view_with_one_non_public_session_created(self):
        """
        This test will create one non public session and test whether it does not show up and shows the proper message instead.
        """
        create_session(is_visible=False) #Creating Session 1
        response = self.client.get(reverse("statisticscore:home"))
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
        session_leipzig_public = create_session() # Creating public Session 1
        response = self.client.get(reverse("statisticscore:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "What's going on in GA?")
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [session_leipzig_public])

    def test_home_view_activity_today_uses_local_dates(self):
        """
        Activity before midnight Berlin time is not today's activity, even though the UTC date is the same.
        """
        berlin = timezone.get_default_timezone()
        now = timezone.make_aware(datetime.datetime(2026, 1, 15, 0, 30), berlin)
        today_session = create_session(name="Today 2026")
        yesterday_session = create_session(name="Yesterday 2026")
        for session, minutes_ago in ((today_session, 10), (yesterday_session, 40)):
            committee = create_committee(session=session)
            with mock.patch('django.utils.timezone.now', return_value=now - datetime.timedelta(minutes=minutes_ago)):
                Point.objects.create(session=session, committee_by=committee)

        with mock.patch('django.utils.timezone.now', return_value=now):
            response = self.client.get(reverse("statisticscore:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_sessions'], [today_session])
