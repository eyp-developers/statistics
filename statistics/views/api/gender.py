import json
from django.http import HttpResponse
from statistics.models import Session, Committee, Gender

def gender_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    gender_points = Gender.objects.filter(committee__session__pk=session_id)

    committees = []
    categories = []
    male = []
    female = []
    other = []

    if gender_points:
        categories.append('Total')
        male.append(gender_points.filter(gender='M').count())
        female.append(gender_points.filter(gender='F').count())
        other.append(gender_points.filter(gender='O').count())

        for point in gender_points:
            if point.committee not in committees:
                committees.append(point.committee)

        for committee in committees:
            categories.append(committee.name)
            male.append(gender_points.filter(committee=committee).filter(gender='M').count())
            female.append(gender_points.filter(committee=committee).filter(gender='F').count())
            other.append(gender_points.filter(committee=committee).filter(gender='O').count())

    gender_json = json.dumps({
        'categories': categories,
        'male': male,
        'female': female,
        'other': other
    })

    return HttpResponse(gender_json, content_type='json')
