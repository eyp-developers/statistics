from django.test import TestCase
from django.urls import reverse

from ..models import ActiveDebate, ContentPoint, Vote
from .helpers import create_session, create_committee, create_user_max


class AllCommitteesFormTests(TestCase):

    def setUp(self):
        self.user = create_user_max()
        self.session = create_session()
        self.session.submission_user = self.user
        self.session.save()
        self.envi = create_committee(session=self.session, name="ENVI")
        self.itre = create_committee(session=self.session, name="ITRE")
        ActiveDebate.objects.create(session=self.session, active_debate="ENVI")
        self.client.force_login(self.user)

    def form_data(self, committee, **data):
        return {'session': self.session.name, 'committee': committee.name, 'debate': 'ENVI', **data}

    def test_all_committees_vote_form_redirects_back_to_itself(self):
        votes = {'in_favour': 8, 'against': 5, 'abstentions': 2, 'absent': 1}
        response = self.client.post(reverse("statisticscore:vote_all", args=[self.session.pk]),
                                    self.form_data(self.itre, **votes), follow=True)
        self.assertRedirects(response, reverse("statisticscore:vote_all", args=[self.session.pk]))
        self.assertContains(response, "Your Committee&#x27;s Votes were successfully submitted")

        vote = Vote.objects.get()
        self.assertEqual(vote.committee_by, self.itre)
        self.assertEqual((vote.in_favour, vote.against, vote.abstentions, vote.absent), (8, 5, 2, 1))

    def test_committee_vote_form_redirects_back_to_itself(self):
        votes = {'in_favour': 1, 'against': 0, 'abstentions': 0, 'absent': 0}
        url = reverse("statisticscore:vote", args=[self.session.pk, self.envi.pk])
        response = self.client.post(url, self.form_data(self.envi, **votes))
        self.assertRedirects(response, url)
        self.assertEqual(Vote.objects.get().committee_by, self.envi)

    def test_all_committees_content_form_redirects_back_to_itself(self):
        response = self.client.post(reverse("statisticscore:content_all", args=[self.session.pk]),
                                    self.form_data(self.itre, point_type='P', content='Energy prices matter'),
                                    follow=True)
        self.assertRedirects(response, reverse("statisticscore:content_all", args=[self.session.pk]))
        self.assertContains(response, "Content Point Successfully Submitted")

        point = ContentPoint.objects.get()
        self.assertEqual(point.committee_by, self.itre)
        self.assertEqual(point.point_content, 'Energy prices matter')

    def test_committee_content_form_redirects_back_to_itself(self):
        url = reverse("statisticscore:content", args=[self.session.pk, self.envi.pk])
        response = self.client.post(url, self.form_data(self.envi, point_type='DR', content='Agreed'))
        self.assertRedirects(response, url)
        self.assertEqual(ContentPoint.objects.get().committee_by, self.envi)
