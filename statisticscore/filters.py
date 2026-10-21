from django.db.models import Q
from django_filters import FilterSet, CharFilter
from .models import Topic


class TopicFilter(FilterSet):
    text = CharFilter(label='Topic Text, Area or Type', method='filter_text')
    committee = CharFilter(label='Committee name', method='filter_committee')

    def get_topic_type(self, full_type):
        for type in Topic.TOPIC_TYPES:
            if full_type.upper() in type[1].upper():
                return type[0]
        return ''

    def filter_text(self, queryset, name, value):
        by_text = queryset.filter(text__icontains=value)
        by_area = queryset.filter(area__icontains=value)
        by_type = queryset.filter(type=self.get_topic_type(value))

        return by_text | by_area | by_type

    def filter_committee(self, queryset, name, value):
        by_statistics_committee = Q(topicplace__statisticstopicplace__committee__name__icontains=value)
        by_historic_committee = Q(topicplace__historictopicplace__historic_committee_name__icontains=value)

        return queryset.filter(by_statistics_committee | by_historic_committee).distinct()

    class Meta:
        model = Topic
        fields = ('text', 'committee')
