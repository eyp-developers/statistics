import datetime
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

from ..models import Session, Committee, ActiveDebate, Point
from .helpers import create_session, create_committee, create_user_max, ips_1_p, lor_1_p


class SessionViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()
        self.session = create_session()

    def test_session_view_with_all_standard_values(self):
        """
        This test makes sure an empty (no committees) session will be shown correctly.
        """
        response = self.client.get(reverse("statisticscore:session", args=[self.session.pk]))
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
        response = self.client.get(reverse("statisticscore:session", args = [self.session.pk]))
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
        response = self.client.get(reverse("statisticscore:session", args = [self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "80th International Session of the European Youth Parliament")
        self.assertContains(response, "ENVI")
        self.assertContains(response, ips_1_p)
        self.assertContains(response, "AFCO")
        self.assertContains(response, lor_1_p)
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")

    def test_session_view_announces_active_debate_just_after_midnight(self):
        """
        Just after midnight Berlin time the UTC date is still yesterday, the banner should show anyway.
        """
        berlin = timezone.get_default_timezone()
        now = timezone.make_aware(datetime.datetime(2026, 1, 15, 0, 30), berlin)
        committee = create_committee(session=self.session)
        ActiveDebate.objects.create(session=self.session, active_debate=committee.name)
        with mock.patch('django.utils.timezone.now', return_value=now - datetime.timedelta(minutes=10)):
            Point.objects.create(session=self.session, committee_by=committee, active_debate=committee.name)

        with mock.patch('django.utils.timezone.now', return_value=now):
            response = self.client.get(reverse("statisticscore:session", args=[self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "is being debated right now!")
