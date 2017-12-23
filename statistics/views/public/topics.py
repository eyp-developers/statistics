from django.shortcuts import render
from statistics.models import Topic


def topics(request):
    topics = Topic.objects.all()
    return render(request, 'statistics/topics.html', {'topics': topics})
