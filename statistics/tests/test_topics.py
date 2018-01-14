from django.test import TestCase
from django.core.urlresolvers import reverse

from ..models import Topic, StatisticsTopic, DatabaseTopic
from helpers import create_session, create_committee


class TopicModelTestCases(TestCase):

    def setUp(self):
        self.session = create_session()
        self.committee = create_committee(session=self.session)

    def test_can_make_statistics_topic(self):
        StatisticsTopic.objects.create(text="This is a topic", type="CR", area="Brexit")
