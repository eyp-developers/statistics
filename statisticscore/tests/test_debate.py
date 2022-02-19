from django.test import TestCase
from django.urls import reverse
from .helpers import create_session, create_committee, create_user_max, ips_1_p

class DebateViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()
        self.session = create_session()
        self.committee = create_committee(session=self.session)

    def test_debate_view_with_no_points(self):
        response = self.client.get(reverse("statisticscore:debate", args=[self.session.pk, self.committee.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debate: ENVI")
        self.assertContains(response, ips_1_p)
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
