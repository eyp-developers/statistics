from django.test import TestCase
from django.urls import reverse

from statisticscore.views import changelog


class HighscoresTests(TestCase):

    def test_highscores_loads(self):
        response = self.client.get(reverse("statisticscore:high_scores"))
        self.assertEqual(response.status_code, 200)
