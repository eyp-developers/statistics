from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from statistics.models import Topic
from statistics.tables import TopicTable
from statistics.filters import TopicFilter

TOPICS_PER_PAGE = 50


class FilteredTopicsListView(SingleTableMixin, FilterView):
    table_class = TopicTable
    model = Topic
    template_name = 'statistics/topics.html'
    filterset_class = TopicFilter
