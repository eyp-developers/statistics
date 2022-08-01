from django.test import TestCase
from django.urls import reverse


class ChangelogTests(TestCase):

    def test_changelog_loads(self):
        response = self.client.get(reverse("statisticscore:changelog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Changelog")
