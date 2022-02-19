import json
from decimal import Decimal
from django.http import HttpResponse
from statisticscore.models import Session, Committee, Point, ContentPoint


def session_api(request, session_id):
    # Since the graphs on the session page need to be able to livereload, we need to create
    # a custom "API" that outputs the neccesary JSON to keep the graph alive

    session = Session.objects.get(pk=session_id)

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id).order_by('name')

    #Then we need all the available points, direct responses and votes
    if session.session_statistics != 'C':
        all_points = Point.objects.filter(session_id=session_id).order_by('timestamp')
        points = Point.objects.filter(session_id=session_id).filter(point_type='P')
        drs = Point.objects.filter(session_id=session_id).filter(point_type='DR')
    else:
        all_points = ContentPoint.objects.filter(session_id=session_id).order_by('timestamp')
        points = ContentPoint.objects.filter(session_id=session_id).filter(point_type='P')
        drs = ContentPoint.objects.filter(session_id=session_id).filter(point_type='DR')

    #Then we need a list of each of them.
    committee_list = []
    points_list = []
    drs_list = []

    if not all_points:
        session_json = json.dumps({
        'committees': '',
        'points': '',
        'drs': '',
        'total_points': '0',
        'type_point': '',
        'type_dr': '',
        'ppm': '',
        })
    else:
        total_points = all_points.count()
        type_point = points.count()
        type_dr = drs.count()
        first_point = all_points.first().timestamp
        latest_point = all_points.last().timestamp
        time_diff = latest_point - first_point
        minutes = (time_diff.days * 1440) + (time_diff.seconds / 60)
        if total_points > 0:
            mpp = Decimal(minutes) / Decimal(total_points)
        else:
            mpp = 0
        #For each committee,
        for committee in committees:
            #Let c be the name
            c = committee.name
            #p be the count of points
            p = points.filter(committee_by=committee).count()
            #and d be the count of DRs.
            d = drs.filter(committee_by=committee).count()

            #Append each newly made variable to our nice lists.
            committee_list.append(c)
            points_list.append(p)
            drs_list.append(d)

        #Finally output the result as JSON
        session_json = json.dumps({
        'committees': committee_list,
        'points': points_list,
        'drs': drs_list,
        'total_points': total_points,
        'type_point': type_point,
        'type_dr': type_dr,
        'mpp': str(round(mpp, 3)),
        })
    return HttpResponse(session_json, content_type='json')
