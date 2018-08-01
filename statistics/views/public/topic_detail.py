from django.views.generic import DetailView
from statistics.models import Topic


class TopicDetail(DetailView):
    model = Topic
    template_name = 'statistics/topic_detail_view.html'
