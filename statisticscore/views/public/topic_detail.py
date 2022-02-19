from django.views.generic import DetailView
from statisticscore.models import Topic


class TopicDetail(DetailView):
    model = Topic
    template_name = 'statisticscore/topic_detail_view.html'
