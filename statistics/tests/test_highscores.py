from django.test import TestCase
from django.urls import reverse

from statistics.views import changelog


class HighscoresTests(TestCase):

    def test_highscores_loads(self):
        response = self.client.get(reverse("statistics:high_scores"))
        self.assertEqual(response.status_code, 200)
