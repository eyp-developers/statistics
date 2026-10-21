import json
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .helpers import create_session, create_committee
from ..models import ActiveDebate, ActiveRound, Point, ContentPoint, Vote, Gender, SubTopic, RunningOrder


class DataEditingPermissionTests(TestCase):
    """
    The data editing APIs may only be used by the admin of the session the data belongs to (or a superuser). The
    submission user may also change a point's subtopics, which the predict page does.
    """

    def setUp(self):
        self.session = create_session(name="Leipzig 2015")
        self.session.admin_user = User.objects.create_user(username='leipzig_admin', password='secret')
        self.session.submission_user = User.objects.create_user(username='leipzig', password='secret')
        self.session.save()
        self.other_session = create_session(name="Berlin 2016")
        self.other_session.admin_user = User.objects.create_user(username='berlin_admin', password='secret')
        self.other_session.save()
        self.superuser = User.objects.create_superuser(username='root', password='secret')

        self.envi = create_committee(self.session, name="ENVI")
        self.afco = create_committee(self.session, name="AFCO")
        ActiveDebate.objects.create(session=self.session, active_debate="ENVI")
        ActiveRound.objects.create(session=self.session, active_round=1)
        self.subtopic = SubTopic.objects.create(session=self.session, committee=self.envi, text="Emissions")
        self.point = Point.objects.create(session=self.session, committee_by=self.afco, active_debate="ENVI", active_round=1)
        self.content = ContentPoint.objects.create(session=self.session, committee_by=self.afco, active_debate="ENVI", point_content="Original")
        self.vote = Vote.objects.create(session=self.session, committee_by=self.afco, active_debate="ENVI", in_favour=10, against=3, abstentions=1, absent=0)
        self.gender = Gender.objects.create(committee=self.envi, gender='F')

    def login(self, user):
        self.client.force_login(user)

    def post_data(self, data):
        return self.client.post(reverse('statisticscore:data_pk_api'), data)

    def delete_vote(self):
        return self.post_data({'delete': 'true', 'data-type': 'vote', 'pk': self.vote.pk})

    def edit_vote(self, session=None):
        return self.post_data({'data-type': 'vote', 'pk': self.vote.pk, 'session': session or self.session.pk,
                               'committee': 'AFCO', 'debate': 'ENVI', 'in_favour': 12, 'against': 3,
                               'abstentions': 1, 'absent': 0})

    def edit_predict(self):
        return self.post_data({'data-type': 'predict', 'pk': self.point.pk,
                               'subtopics': json.dumps([{'pk': self.subtopic.pk}]), 'all_subtopics': '[]'})

    def post_running_order(self, data):
        return self.client.post(reverse('statisticscore:runningorder_api', args=[self.session.pk]), data)

    def assert_refused(self, response):
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', response.json())

    def test_anonymous_visitor_cannot_change_any_data(self):
        self.assert_refused(self.delete_vote())
        self.assert_refused(self.edit_vote())
        self.assert_refused(self.edit_predict())
        for data_type, obj in [('point', self.point), ('content', self.content), ('gender', self.gender)]:
            self.assert_refused(self.post_data({'delete': 'true', 'data-type': data_type, 'pk': obj.pk}))
        self.assertTrue(Vote.objects.filter(pk=self.vote.pk, in_favour=10).exists())
        self.assertEqual(Point.objects.count(), 1)
        self.assertEqual(ContentPoint.objects.count(), 1)
        self.assertEqual(Gender.objects.count(), 1)
        self.assertEqual(self.point.subtopics.count(), 0)

    def test_anonymous_visitor_cannot_change_the_running_order(self):
        self.assert_refused(self.post_running_order({'by': self.afco.pk, 'type': 'P'}))
        self.assertEqual(RunningOrder.objects.count(), 0)

    def test_other_sessions_admin_cannot_change_data(self):
        self.login(self.other_session.admin_user)
        self.assert_refused(self.delete_vote())
        self.assert_refused(self.edit_vote())
        self.assert_refused(self.edit_vote(session=self.other_session.pk))
        self.assert_refused(self.edit_predict())
        self.assert_refused(self.post_running_order({'by': self.afco.pk, 'type': 'P'}))
        self.assertTrue(Vote.objects.filter(pk=self.vote.pk, in_favour=10).exists())
        self.assertEqual(RunningOrder.objects.count(), 0)

    def test_admin_cannot_move_data_into_another_session(self):
        self.login(self.session.admin_user)
        self.assert_refused(self.edit_vote(session=self.other_session.pk))

    def test_submission_user_can_only_change_predicted_subtopics(self):
        self.login(self.session.submission_user)
        self.assert_refused(self.delete_vote())
        self.assert_refused(self.edit_vote())
        self.assert_refused(self.post_running_order({'by': self.afco.pk, 'type': 'P'}))
        self.assert_refused(self.post_data({'delete': 'true', 'data-type': 'predict', 'pk': self.point.pk}))

        response = self.edit_predict()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['subtopics'], 'Emissions')
        self.assertEqual(list(self.point.subtopics.all()), [self.subtopic])

    def test_own_admin_can_change_data(self):
        self.login(self.session.admin_user)
        response = self.edit_vote()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['in_favour'], 12)
        self.assertEqual(self.edit_predict().status_code, 200)

        response = self.post_data({'delete': 'true', 'data-type': 'gender', 'pk': self.gender.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Gender.objects.count(), 0)
        self.assertEqual(self.delete_vote().status_code, 200)
        self.assertEqual(Vote.objects.count(), 0)

        self.assertEqual(self.post_running_order({'by': self.afco.pk, 'type': 'P'}).status_code, 200)
        self.assertEqual(RunningOrder.objects.count(), 1)

    def test_superuser_can_change_data(self):
        self.login(self.superuser)
        self.assertEqual(self.edit_vote().status_code, 200)
        self.assertEqual(self.post_running_order({'by': self.afco.pk, 'type': 'P'}).status_code, 200)
        self.assertEqual(self.delete_vote().status_code, 200)

    def test_unknown_data_is_rejected(self):
        self.login(self.session.admin_user)
        self.assertEqual(self.post_data({'delete': 'true', 'data-type': 'vote', 'pk': 999999}).status_code, 404)
        self.assertEqual(self.post_data({'delete': 'true', 'data-type': 'nonsense', 'pk': 1}).status_code, 400)

    def test_reading_stays_public(self):
        response = self.client.get(reverse('statisticscore:data_pk_api'), {'data_type': 'vote', 'pk': self.vote.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['in_favour'], 10)
        # A session without points, because the running order API can't yet read one with points (known bug 5).
        ActiveDebate.objects.create(session=self.other_session)
        ActiveRound.objects.create(session=self.other_session)
        response = self.client.get(reverse('statisticscore:runningorder_api', args=[self.other_session.pk]))
        self.assertEqual(response.status_code, 200)
