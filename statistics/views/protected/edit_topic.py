from django.urls import reverse_lazy
from django.views.generic import UpdateView
from statistics.models import Topic


class TopicUpdate(UpdateView):
    model = Topic
    fields = ['text', 'type', 'area', 'difficulty']
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('statistics:topics')
