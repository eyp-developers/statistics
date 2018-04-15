import django_tables2 as tables
from .models import Topic
from django.utils.html import format_html, format_html_join
from django.urls import reverse


class TopicTable(tables.Table):
    committee = tables.Column(empty_values=())
    used_at = tables.Column(empty_values=(), attrs={'td': {'style': 'text-align: center'}})
    text = tables.Column(attrs={'td': {'style': 'font-size: 14px'}})
    extra = tables.Column(empty_values=(), attrs={'td': {'style': 'font-size: 14px'}})

    def render_extra(self, record):
        extras = []
        if record.area:
            extras.append(('Area:', record.area))
        if record.type:
            type = next(t[1] for t in Topic.TOPIC_TYPES if t[0] == record.type)
            extras.append(('Type:', type))
        if record.difficulty:
            difficulty = next(d[1] for d in Topic.DIFFICULTIES if d[0] == record.difficulty)
            extras.append(('Difficulty: ', difficulty))

        return format_html_join(', ', '<b>{}</b> {}', extras)

    def render_committee(self, record):
        places = record.topicplace_set.all()
        committee_names = set([p.committee_name() for p in places])

        return ", ".join(committee_names)

    def render_used_at(self, record):
        places = record.topicplace_set.all()
        committees = []
        for place in places:
            if hasattr(place, 'statisticstopicplace'):
                committees.append(place.statisticstopicplace.committee)

        committee_links = format_html_join(
                '\n', '<a class="btn btn-primary" href="{}" role="button">{}</a>',
                ((reverse('statistics:debate', args=[c.session.id, c.id]), c.session.name) for c in committees)
            )

        historic_places = []
        for place in places:
            if hasattr(place, 'historictopicplace'):
                historic_places.append(place.historictopicplace)

        historic_places_html = format_html_join(
            '', '<p>{}</p>', ((str(h),) for h in historic_places)
        )
        return format_html("{} {}", committee_links, historic_places_html)

    class Meta:
        model = Topic
        exclude = ('id', 'type', 'area', 'difficulty')
        sequence = ('text', 'committee', 'used_at')
        template_name = 'django_tables2/bootstrap.html'
