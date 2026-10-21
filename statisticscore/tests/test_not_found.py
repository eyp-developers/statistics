from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from ..views.public_views import handler500
from .helpers import create_session, create_committee

UNKNOWN_ID = 999999


class UnknownIdTests(TestCase):
    """
    Unknown or deleted sessions and committees in the URL should give a 404, not a 500.
    """

    def setUp(self):
        self.session = create_session()
        self.committee = create_committee(session=self.session)
        self.other_session = create_session(name="Berlin 2016")
        self.other_committee = create_committee(session=self.other_session, name="AFCO")

    def assertNotFound(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404, url)

    def test_public_pages_with_unknown_session(self):
        self.assertNotFound(reverse("statisticscore:session", args=[UNKNOWN_ID]))
        self.assertNotFound(reverse("statisticscore:debate", args=[UNKNOWN_ID, self.committee.pk]))

    def test_debate_page_with_unknown_committee(self):
        self.assertNotFound(reverse("statisticscore:debate", args=[self.session.pk, UNKNOWN_ID]))

    def test_debate_page_with_committee_of_another_session(self):
        self.assertNotFound(reverse("statisticscore:debate", args=[self.session.pk, self.other_committee.pk]))

    def test_session_apis_with_unknown_session(self):
        for name in ["session_api", "runningorder_api", "active_debate_api", "gender_api", "committees_api"]:
            self.assertNotFound(reverse("statisticscore:" + name, args=[UNKNOWN_ID]))

    def test_debate_apis_with_unknown_session_or_committee(self):
        for name in ["debate_api", "debate_vote_api", "content_api", "content_latest_api"]:
            self.assertNotFound(reverse("statisticscore:" + name, args=[UNKNOWN_ID, self.committee.pk]))
            self.assertNotFound(reverse("statisticscore:" + name, args=[self.session.pk, UNKNOWN_ID]))

    def test_committees_api_with_unknown_committee(self):
        url = reverse("statisticscore:committees_api", args=[self.session.pk])
        self.assertNotFound(url + "?pk=%d" % UNKNOWN_ID)


@override_settings(DEBUG=False)
class ErrorPageTests(TestCase):

    def test_custom_404_page_has_status_404(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Error 404: Page not Found", status_code=404)

    def test_unknown_session_shows_custom_404_page(self):
        response = self.client.get(reverse("statisticscore:session", args=[UNKNOWN_ID]))
        self.assertContains(response, "Error 404: Page not Found", status_code=404)

    def test_custom_500_page_has_status_500(self):
        response = handler500(RequestFactory().get("/"))
        self.assertEqual(response.status_code, 500)
