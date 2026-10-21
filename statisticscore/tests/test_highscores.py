from django.test import TestCase
from django.urls import reverse

from statisticscore.models import Point, Vote
from .helpers import create_session, create_committee


def add_point(session, committee):
    return Point.objects.create(session=session, committee_by=committee, active_debate=committee.name)


def add_vote(session, committee, in_favour, against, abstentions=0, absent=0):
    return Vote.objects.create(session=session, committee_by=committee, active_debate=committee.name,
                               in_favour=in_favour, against=against, abstentions=abstentions, absent=absent)


class HighscoresTests(TestCase):

    def get_high_scores(self):
        response = self.client.get(reverse("statisticscore:high_scores"))
        self.assertEqual(response.status_code, 200)
        return response

    def ranked_sessions(self, response):
        return [name for name, _ in response.context['top_voters']]

    def test_highscores_loads(self):
        self.get_high_scores()

    def test_session_with_points_appears(self):
        session = create_session(name="With Points")
        committee = create_committee(session)
        add_point(session, committee)
        add_vote(session, committee, in_favour=10, against=5)

        response = self.get_high_scores()
        self.assertEqual(response.context['top_voters'], [("With Points", 15)])
        self.assertEqual(response.context['top_points'], [("With Points", 1)])

    def test_visible_session_without_points_does_not_appear(self):
        # The session with points is created first, so an earlier session's points must not
        # qualify the sessions that come after it.
        with_points = create_session(name="With Points")
        committee = create_committee(with_points)
        add_point(with_points, committee)
        add_vote(with_points, committee, in_favour=10, against=5)

        without_points = create_session(name="Without Points")
        committee = create_committee(without_points)
        add_vote(without_points, committee, in_favour=20, against=20)

        response = self.get_high_scores()
        self.assertEqual(self.ranked_sessions(response), ["With Points"])
        for key in ('top_in_favour', 'top_against', 'top_points', 'top_drs', 'top_points_in_debate',
                    'top_drs_in_debate', 'top_successful', 'top_unsuccessful', 'top_mpp'):
            for name, _ in response.context[key]:
                self.assertNotIn("Without Points", name, key)

    def test_hidden_and_technical_problem_sessions_never_appear(self):
        visible = create_session(name="Visible")
        hidden = create_session(name="Hidden", is_visible=False)
        broken = create_session(name="Broken")
        broken.has_technical_problems = True
        broken.save()
        for session in (visible, hidden, broken):
            committee = create_committee(session)
            add_point(session, committee)
            add_vote(session, committee, in_favour=30, against=10)

        response = self.get_high_scores()
        self.assertEqual(self.ranked_sessions(response), ["Visible"])
        self.assertNotContains(response, "Hidden")
        self.assertNotContains(response, "Broken")

    def test_unanimous_session_ranks_in_favour(self):
        unanimous = create_session(name="Unanimous")
        committee = create_committee(unanimous)
        add_point(unanimous, committee)
        add_vote(unanimous, committee, in_favour=20, against=0)

        split = create_session(name="Split")
        committee = create_committee(split)
        add_point(split, committee)
        add_vote(split, committee, in_favour=10, against=10)

        response = self.get_high_scores()
        self.assertEqual(response.context['top_in_favour'], [("Unanimous", 100), ("Split", 50)])
        self.assertEqual(response.context['top_against'], [("Split", 50), ("Unanimous", 0)])
