from django.shortcuts import render

def committee(request, session_id, committee_id):
    # The idea is not only to have a "debate page", where you can see how many points are made during the debate of a particular resolution,
    # but also for there to be a "committee page", where delegates can see how many points their
    # committee has made during each debate, what was the longest time between points etc.
    # This should be made in due time.
    pass


def handler404(request):
    return render(request, 'statistics/404.html')


def handler500(request):
    return render(request, 'statistics/500.html')
