from django.test import TestCase
from django.core.urlresolvers import reverse

from views.public_views import home

# Create your tests here.


class HomeViewTests(TestCase):

    def test_home_view__without_any_sessions_created(self):
        """
        If no sessions exist the appropriate message should be shown.
        """
        response = self.client.get(reverse("statistics:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No sessions are available.")
        self.assertContains(response, "Account")
        self.assertContains(response, "Login")
        self.assertQuerysetEqual(response.context['latest_sessions_list'], [])

    def test_home_view_with_one_session_created(self):
        pass
