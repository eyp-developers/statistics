from django.test import TestCase
from django.core.urlresolvers import reverse

from statistics.views import changelog


class ChangelogTests(TestCase):

    def test_changelog_loads(self):
        response = self.client.get(reverse("statistics:changelog"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Changelog")
