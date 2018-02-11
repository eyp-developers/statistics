from django_filters import FilterSet, CharFilter
from .models import Topic, StatisticsTopicPlace, HistoricTopicPlace


class TopicFilter(FilterSet):
    text = CharFilter(lookup_expr='icontains')
    committee = CharFilter(label='Committee name', lookup_expr='icontains', method='filter_committee')

    def filter_committee(self, queryset, name, value):
        print(queryset, name, value)

        place_ids = [topic.id for topic in StatisticsTopicPlace.objects.all()
                     if str(value).upper() in topic.committee_name().upper()]

        place_ids = place_ids + [topic.id for topic in HistoricTopicPlace.objects.all()
                     if str(value).upper() in topic.committee_name().upper()]

        return queryset.filter(topicplace__in=place_ids)

    class Meta:
        model = Topic
        fields = ('text', 'committee', 'type', 'area', 'difficulty')
