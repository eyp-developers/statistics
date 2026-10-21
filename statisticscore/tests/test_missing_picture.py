import shutil
import tempfile

from django.test import TestCase, override_settings
from django.urls import reverse

from .helpers import create_session, create_committee


class MissingSessionPictureTests(TestCase):
    """
    A session whose picture file has gone missing should still render, just without the picture.
    """

    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_root)
        self.settings_override.enable()
        self.session = create_session()
        self.committee = create_committee(session=self.session)
        self.session.picture.storage.delete(self.session.picture.name)

    def tearDown(self):
        self.settings_override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_home_view_with_missing_picture(self):
        response = self.client.get(reverse("statisticscore:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")
        self.assertContains(response, "background: #253746 url('')")

    def test_session_view_with_missing_picture(self):
        response = self.client.get(reverse("statisticscore:session", args=[self.session.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Leipzig 2015")

    def test_debate_view_with_missing_picture(self):
        response = self.client.get(reverse("statisticscore:debate", args=[self.session.pk, self.committee.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debate: ENVI")
