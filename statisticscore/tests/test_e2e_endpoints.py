import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from ..models import ActiveDebate, ActiveRound, Committee, Point, Session, SubTopic, Vote

TOKEN = 'test-token'


@override_settings(E2E_ENDPOINTS_ENABLED=True, E2E_TOKEN=TOKEN, E2E_ALLOW_RESET=False)
class E2EEndpointTests(TestCase):

    def post(self, name, data=None, token=TOKEN, args=None):
        return self.client.post(reverse(name, args=args), json.dumps(data or {}),
                                content_type='application/json', HTTP_X_E2E_TOKEN=token)

    def create_session(self, **data):
        data.setdefault('name', 'E2E Berlin 2026')
        response = self.post('e2e:create_session', data)
        self.assertEqual(response.status_code, 201)
        return response.json()

    @override_settings(E2E_ENDPOINTS_ENABLED=False)
    def test_endpoints_are_hidden_when_disabled(self):
        """
        With the setting off (the default) the endpoints must look like they don't exist, even with the right token.
        """
        response = self.client.get(reverse('e2e:health'), HTTP_X_E2E_TOKEN=TOKEN)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.post('e2e:create_session', {'name': 'Nope'}).status_code, 404)
        self.assertFalse(Session.objects.exists())

    def test_wrong_or_missing_token_is_rejected(self):
        self.assertEqual(self.client.get(reverse('e2e:health')).status_code, 404)
        self.assertEqual(self.client.get(reverse('e2e:health'), HTTP_X_E2E_TOKEN='wrong').status_code, 404)
        self.assertEqual(self.client.get(reverse('e2e:health'), HTTP_X_E2E_TOKEN=TOKEN).status_code, 200)

    @override_settings(E2E_TOKEN='')
    def test_empty_token_setting_never_matches(self):
        response = self.client.get(reverse('e2e:health'), HTTP_X_E2E_TOKEN='')
        self.assertEqual(response.status_code, 404)

    def test_create_session_with_committees(self):
        data = self.create_session(mode='C', visible=True, active_debate='ENVI', active_round=2, committees=[
            {'name': 'ENVI', 'topic': 'Climate', 'subtopics': ['Emissions', 'Energy']},
            {'name': 'AFCO', 'topic': 'Democracy'},
        ])

        session = Session.objects.get(pk=data['id'])
        self.assertEqual(session.session_statistics, 'C')
        self.assertTrue(session.is_visible)
        self.assertEqual(data['admin']['username'], 'e2eberlin2026_admin')
        self.assertEqual(data['submission']['username'], 'e2eberlin2026')
        self.assertIsNotNone(authenticate(username='e2eberlin2026_admin', password=data['admin']['password']))
        self.assertIsNotNone(authenticate(username='e2eberlin2026', password=data['submission']['password']))

        self.assertEqual([c['name'] for c in data['committees']], ['ENVI', 'AFCO'])
        self.assertEqual([s['text'] for s in data['committees'][0]['subtopics']], ['General', 'Emissions', 'Energy'])
        self.assertEqual(SubTopic.objects.filter(committee__session=session).count(), 4)
        self.assertEqual(ActiveDebate.objects.get(session=session).active_debate, 'ENVI')
        self.assertEqual(ActiveRound.objects.get(session=session).active_round, 2)

    def test_duplicate_session_name_is_rejected(self):
        self.create_session(name='E2E Berlin 2026')
        response = self.post('e2e:create_session', {'name': 'e2e berlin 2026'})
        self.assertEqual(response.status_code, 409)
        self.assertEqual(Session.objects.count(), 1)

    def test_session_state(self):
        data = self.create_session(committees=[{'name': 'ENVI'}])
        response = self.post('e2e:session_state', {'active_debate': 'ENVI', 'visible': True}, args=[data['id']])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['active_debate'], 'ENVI')
        self.assertTrue(Session.objects.get(pk=data['id']).is_visible)

    def test_session_data(self):
        data = self.create_session(active_debate='ENVI', active_round=2, committees=[
            {'name': 'ENVI', 'subtopics': ['Emissions']}, {'name': 'AFCO'}])
        response = self.post('e2e:session_data', {
            'points': [{'committee': 'AFCO', 'subtopics': ['Emissions']},
                       {'committee': 'AFCO', 'type': 'DR', 'round': 1, 'minutes_ago': 30}],
            'content': [{'committee': 'AFCO', 'text': 'We should act'}],
            'votes': [{'committee': 'AFCO', 'in_favour': 5, 'against': 2}],
            'genders': [{'committee': 'ENVI', 'gender': 'F'}],
        }, args=[data['id']])
        self.assertEqual(response.status_code, 201)
        created = response.json()
        self.assertEqual([len(created[k]) for k in ['points', 'content', 'votes', 'genders']], [2, 1, 1, 1])

        first, second = Point.objects.filter(pk__in=created['points']).order_by('pk')
        self.assertEqual((first.active_debate, first.active_round), ('ENVI', 2))
        self.assertEqual([s.text for s in first.subtopics.all()], ['Emissions'])
        self.assertEqual((second.point_type, second.active_round), ('DR', 1))
        self.assertLess(second.timestamp, first.timestamp)
        self.assertEqual(Vote.objects.get().total_votes(), 7)

    def test_login_as_session_admin(self):
        data = self.create_session()
        response = self.post('e2e:login', {'session_id': data['id'], 'role': 'admin'})
        self.assertEqual(response.json()['username'], data['admin']['username'])
        # The login sticks to the client, so a protected admin page now renders.
        overview = self.client.get(reverse('statisticscore:overview', args=[data['id']]))
        self.assertEqual(overview.status_code, 200)

    def test_delete_session_removes_its_users_and_data(self):
        data = self.create_session(committees=[{'name': 'ENVI'}])
        response = self.client.delete(reverse('e2e:delete_session', args=[data['id']]), HTTP_X_E2E_TOKEN=TOKEN)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Session.objects.exists())
        self.assertFalse(Committee.objects.exists())
        self.assertFalse(User.objects.exists())
        # Deleting again is fine, so test cleanup can always run.
        response = self.client.delete(reverse('e2e:delete_session', args=[data['id']]), HTTP_X_E2E_TOKEN=TOKEN)
        self.assertEqual(response.status_code, 204)

    def test_reset_needs_its_own_setting(self):
        self.create_session()
        self.assertEqual(self.post('e2e:reset').status_code, 403)
        self.assertTrue(Session.objects.exists())

        with self.settings(E2E_ALLOW_RESET=True):
            self.assertEqual(self.post('e2e:reset').status_code, 204)
        self.assertFalse(Session.objects.exists())
