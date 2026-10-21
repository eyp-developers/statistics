import json
from django.test import TestCase
from django.urls import reverse
from .helpers import create_session, create_committee
from ..models import ActiveDebate, ActiveRound, Point, RunningOrder, SubTopic

class RunningOrderApiTests(TestCase):

    def setUp(self):
        self.session = create_session()
        self.envi = create_committee(session=self.session, name="ENVI")
        self.afco = create_committee(session=self.session, name="AFCO")
        ActiveDebate.objects.create(session=self.session, active_debate="ENVI")
        ActiveRound.objects.create(session=self.session, active_round=1)
        self.url = reverse("statisticscore:runningorder_api", args=[self.session.pk])

    def create_point(self, committee, point_type="P"):
        return Point.objects.create(session=self.session, committee_by=committee, active_debate="ENVI", active_round=1, point_type=point_type)

    def test_api_without_points(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([c["height"] for c in json.loads(response.content)["committees"]], [75, 75])

    def test_api_with_points(self):
        self.create_point(self.afco)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        heights = {c["pk"]: c["height"] for c in json.loads(response.content)["committees"]}
        self.assertEqual(heights[self.envi.pk], 100.0)
        self.assertEqual(heights[self.afco.pk], 95.0)

    def test_recognising_direct_response_copies_previous_subtopics(self):
        subtopic = SubTopic.objects.create(session=self.session, committee=self.envi, text="Trade")
        previous = self.create_point(self.envi)
        previous.subtopics.add(subtopic)
        RunningOrder.objects.create(session=self.session, position=1, committee_by=self.afco, point_type="DR")

        response = self.client.post(self.url, {"action": "R"})

        self.assertEqual(response.status_code, 200)
        recognised = Point.objects.filter(session=self.session).latest("pk")
        self.assertEqual(recognised.committee_by, self.afco)
        self.assertEqual(recognised.point_type, "DR")
        self.assertEqual(list(recognised.subtopics.all()), [subtopic])
        self.assertFalse(RunningOrder.objects.filter(session=self.session).exists())
