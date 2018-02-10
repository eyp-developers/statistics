import django_tables2 as tables
from .models import Topic


class TopicTable(tables.Table):
    class Meta:
        model = Topic
        template_name = 'django_tables2/bootstrap.html'
