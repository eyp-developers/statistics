from django.shortcuts import render


def get_started(request):
    return render(request, 'statisticscore/get_started.html')
