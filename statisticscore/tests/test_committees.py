import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Committee, SubTopic
from .helpers import create_session, create_committee


class CreateCommitteeAuthorizationTests(TestCase):

    def setUp(self):
        self.session = create_session()
        self.other_session = create_session(name="Berlin 2016")
        self.admin = User.objects.create_user(username='leipzig', password='top_secret')
        self.submission = User.objects.create_user(username='leipzig_submit', password='top_secret')
        self.other_admin = User.objects.create_user(username='berlin', password='top_secret')
        self.session.admin_user = self.admin
        self.session.submission_user = self.submission
        self.session.save()
        self.other_session.admin_user = self.other_admin
        self.other_session.save()
        self.committee = create_committee(self.session, name="ENVI")
        self.other_committee = create_committee(self.other_session, name="AFCO")

    def post(self, session, data):
        return self.client.post(reverse('statisticscore:create_committee', args=[session.pk]), data)

    def delete(self, session, committee):
        return self.post(session, {'delete': 'true', 'pk': committee.pk})

    def edit(self, session, pk, name='CLIM'):
        return self.post(session, {'pk': pk, 'name': name, 'topic': 'A topic',
                                   'subtopics': json.dumps([{'pk': '', 'subtopic': 'General'}])})

    def assertForbidden(self, response):
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('msg', response.json())

    def test_other_sessions_admin_cannot_delete_or_edit(self):
        self.client.force_login(self.other_admin)
        self.assertForbidden(self.delete(self.session, self.committee))
        self.assertForbidden(self.edit(self.session, self.committee.pk))
        self.assertForbidden(self.edit(self.session, ''))
        self.committee.refresh_from_db()
        self.assertEqual(self.committee.name, 'ENVI')
        self.assertEqual(Committee.objects.filter(session=self.session).count(), 1)

    def test_submission_user_cannot_delete_or_edit(self):
        self.client.force_login(self.submission)
        self.assertForbidden(self.delete(self.session, self.committee))
        self.assertForbidden(self.edit(self.session, self.committee.pk))
        self.committee.refresh_from_db()
        self.assertEqual(self.committee.name, 'ENVI')

    def test_own_admin_can_create_edit_and_delete(self):
        self.client.force_login(self.admin)
        response = self.edit(self.session, '', name='AGRI')
        self.assertEqual(response.status_code, 200)
        new_committee = Committee.objects.get(pk=response.json()['pk'])
        self.assertEqual(new_committee.session, self.session)
        self.assertEqual(SubTopic.objects.filter(committee=new_committee).count(), 1)

        response = self.edit(self.session, self.committee.pk)
        self.assertEqual(response.status_code, 200)
        self.committee.refresh_from_db()
        self.assertEqual(self.committee.name, 'CLIM')

        response = self.delete(self.session, self.committee)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Committee.objects.filter(pk=self.committee.pk).exists())

    def test_superuser_can_delete(self):
        self.client.force_login(User.objects.create_superuser(username='root', password='top_secret'))
        self.assertEqual(self.delete(self.session, self.committee).status_code, 200)
        self.assertFalse(Committee.objects.filter(pk=self.committee.pk).exists())

    def test_admin_cannot_touch_committee_of_another_session_through_own_session(self):
        """
        Posting another session's committee pk to your own session's URL must not delete it or move it over.
        """
        self.client.force_login(self.admin)
        self.assertForbidden(self.delete(self.session, self.other_committee))
        self.assertForbidden(self.edit(self.session, self.other_committee.pk))
        self.other_committee.refresh_from_db()
        self.assertEqual(self.other_committee.name, 'AFCO')
        self.assertEqual(self.other_committee.session, self.other_session)

    def test_delete_without_valid_pk_is_rejected(self):
        self.client.force_login(self.admin)
        self.assertForbidden(self.post(self.session, {'delete': 'true', 'pk': ''}))
        self.assertForbidden(self.post(self.session, {'delete': 'true', 'pk': 'abc'}))
        self.assertTrue(Committee.objects.filter(pk=self.committee.pk).exists())
