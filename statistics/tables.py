import django_tables2 as tables
from .models import Topic
from django.utils.html import format_html, format_html_join
from django.urls import reverse


class TopicTable(tables.Table):
    committee = tables.Column(empty_values=())
    used_at = tables.Column(empty_values=())

    def render_committee(self, record):
        places = record.topicplace_set.all()

        if len(places) == 1:
            return places[0].committee_name()

        committees = ''
        for place in places:
            committees += place.committee_name() + ', '

        return committees

    def render_used_at(self, record):
        places = record.topicplace_set.all()
        committees = []
        for place in places:
            if hasattr(place, 'statisticstopicplace'):
                committees.append(place.statisticstopicplace.committee)

        committee_links = format_html_join(
                '\n', '<a class="btn btn-primary" href="{}" role="button">{}</a>',
                ((reverse('statistics:debate', args=[c.session.id, c.id]), c.name) for c in committees)
            )

        return committee_links

    class Meta:
        model = Topic
        exclude = ('id',)
        sequence = ('text', 'committee', 'type', 'area', 'difficulty', 'used_at')
        template_name = 'django_tables2/bootstrap.html'
