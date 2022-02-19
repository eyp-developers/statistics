from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from statisticscore.models import Topic
from statisticscore.tables import TopicTable
from statisticscore.filters import TopicFilter

TOPICS_PER_PAGE = 50


class FilteredTopicsListView(SingleTableMixin, FilterView):
    table_class = TopicTable
    model = Topic
    template_name = 'statisticscore/topics.html'
    filterset_class = TopicFilter
