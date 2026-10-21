from django.test import TestCase
from django.urls import reverse

from ..filters import TopicFilter
from ..models import Topic, StatisticsTopicPlace, HistoricTopicPlace
from .helpers import create_session, create_committee


class TopicModelTestCases(TestCase):

    def setUp(self):
        self.session = create_session()
        self.committee = create_committee(session=self.session)

    def test_can_make_topic(self):
        Topic.objects.create(text="This is a topic", type="CR", area="Brexit")


class TopicFilterTestCases(TestCase):

    def setUp(self):
        session = create_session()
        self.statistics_topic = Topic.objects.create(text="Statistics committee topic")
        StatisticsTopicPlace.objects.create(topic=self.statistics_topic, committee=create_committee(session=session, name="SEDE"))
        self.historic_topic = Topic.objects.create(text="Historic committee topic")
        HistoricTopicPlace.objects.create(topic=self.historic_topic, historic_committee_name="AFCO")
        self.other_topic = Topic.objects.create(text="Other topic")
        StatisticsTopicPlace.objects.create(topic=self.other_topic, committee=create_committee(session=session, name="ENVI"))

    def filtered_topics(self, committee):
        return list(TopicFilter({'committee': committee}, queryset=Topic.objects.all()).qs)

    def test_filters_by_statistics_committee_name(self):
        self.assertEqual(self.filtered_topics("sed"), [self.statistics_topic])

    def test_filters_by_historic_committee_name(self):
        self.assertEqual(self.filtered_topics("afc"), [self.historic_topic])

    def test_lists_topic_once_when_used_in_several_matching_committees(self):
        HistoricTopicPlace.objects.create(topic=self.statistics_topic, historic_committee_name="SEDE I")
        self.assertEqual(self.filtered_topics("SEDE"), [self.statistics_topic])

    def test_topics_page_filters_by_committee_name(self):
        response = self.client.get(reverse('statisticscore:topics'), {'committee': 'SEDE'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.statistics_topic.text)
        self.assertNotContains(response, self.other_topic.text)
