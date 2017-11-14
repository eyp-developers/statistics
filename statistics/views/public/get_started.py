from django.shortcuts import render


def get_started(request):
    return render(request, 'statistics/get_started.html')
