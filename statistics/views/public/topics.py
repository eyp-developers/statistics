from django.shortcuts import render
from statistics.models import Topic
from statistics.tables import TopicTable


def topics(request):
    table = TopicTable(Topic.objects.all())
    return render(request, 'statistics/topics.html', {'table': table})
