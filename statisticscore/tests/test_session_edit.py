from django.test import TestCase
from django.urls import reverse

from .helpers import create_session, create_user_max


class SessionEditViewTests(TestCase):

    def setUp(self):
        self.user = create_user_max()
        self.session = create_session(statistics_type="C")
        self.session.admin_user = self.user
        self.session.save()
        self.client.force_login(self.user)

    def test_edit_view_selects_current_statistics_mode(self):
        """
        This test makes sure the edit form is pre-filled with the session's current statistics mode.
        """
        response = self.client.get(reverse("statisticscore:edit", args=[self.session.pk]))
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form['statistics'].value(), "C")
        self.assertNotIn('statistics', form.errors)
        self.assertContains(response, '<option value="C" selected>Point Content Only</option>')
