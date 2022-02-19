from django.test import TestCase
from django.urls import reverse
from .helpers import create_user_max


class LoginViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()

    def test_login_view_loads_properly(self):
        """
        This test will see whether the login view contains the necessary elements needed to log in a user.
        """
        response = self.client.get(reverse("statisticscore:login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
