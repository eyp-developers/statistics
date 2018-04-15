from django_filters import FilterSet, CharFilter
from .models import Topic, StatisticsTopicPlace, HistoricTopicPlace


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
        # Warning: important to format string in this fashion to prevent SQL injection
        topics_by_committee_name = Topic.objects.raw("\
            SELECT * FROM statistics_topic AS t \
            JOIN ( \
                SELECT topic_id FROM ( \
                    SELECT topicplace_ptr_id \
                    FROM statistics_statisticstopicplace AS sp \
                    JOIN statistics_committee AS c \
                    ON sp.committee_id=c.id \
                    WHERE c.name ILIKE '%%' || %s || '%%' \
                    UNION \
                    SELECT topicplace_ptr_id \
                    FROM statistics_historictopicplace AS hp \
                    WHERE hp.historic_committee_name ILIKE '%%' || %s || '%%' \
                ) AS tp_ptrs \
                JOIN statistics_topicplace AS tp \
                ON tp_ptrs.topicplace_ptr_id = tp.id \
            ) AS fp \
            ON t.id = fp.topic_id \
        ", [value, value])

        committee_name_topic_ids = [t.id for t in topics_by_committee_name]

        return queryset.filter(topicplace__in=committee_name_topic_ids)

    class Meta:
        model = Topic
        fields = ('text', 'committee')
