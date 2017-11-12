import json
from django.http import HttpResponse
from statistics.models import Session, Committee, ActiveDebate

def active_debate_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.get(session=session)
    active_committee = Committee.objects.filter(session=session).filter(name=active_debate.active_debate)[0]

    active_debate_json = json.dumps({
    'active_debate_pk': active_committee.pk,
    'active_session_pk': session.pk
    })
    return HttpResponse(active_debate_json, content_type='json')
