import django_tables2 as tables
from .models import Topic


class TopicTable(tables.Table):
    committee = tables.Column(empty_values=())

    def render_committee(self, record):
        places = record.topicplace_set.all()

        if len(places) == 1:
            return places[0].committee_name()

        committees = ''
        for place in places:
            committees += place.committee_name() + ', '

        return committees

    class Meta:
        model = Topic
        exclude = ('id',)
        sequence = ('text', 'committee', 'type', 'area', 'difficulty')
        template_name = 'django_tables2/bootstrap.html'
