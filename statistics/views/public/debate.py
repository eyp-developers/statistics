from django.shortcuts import render
from statistics.models import Session, Committee, Point, ContentPoint, Vote


def debate(request, session_id, committee_id):
    # Same for debates as for sessions, the only static content is the name and data of the committee and the session.
    # The rest of the point/voting data comes through the api that can constantly be updated.
    c = Committee.objects.get(pk=committee_id)
    s = Session.objects.get(pk=session_id)
    # The statistics_type will let us render different templates based on the statistics selected by the user.
    statistics_type = s.session_statistics

    no_stats = True
    # Getting the latest of everything to check if the date of them was today.
    no_stats = (len(Point.objects.filter(session=s))
                or len(ContentPoint.objects.filter(session=s))
                or len(Vote.objects.filter(session=s)))

    # The voting enabled option lets us change the html content and js so that the voting is not displayed.
    voting_enabled = s.voting_enabled
    context = {'committee': c, 'session': s, 'statistics_type': statistics_type,
               'voting_enabled': voting_enabled, 'no_stats': no_stats}

    if statistics_type == 'JF':  # Should use or statement
        return render(request, 'statistics/joint.html', context)
    elif statistics_type == 'SF':
        return render(request, 'statistics/joint.html', context)
    elif statistics_type == 'S':
        return render(request, 'statistics/statistics.html', context)
    elif statistics_type == 'C':
        return render(request, 'statistics/content.html', context)
    elif statistics_type == 'R':
        return render(request, 'statistics/statistics.html', context)
    elif statistics_type == 'RC':
        return render(request, 'statistics/joint.html', context)
