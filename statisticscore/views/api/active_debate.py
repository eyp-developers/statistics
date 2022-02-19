import json
from django.http import HttpResponse
from statisticscore.models import Session, Committee, ActiveDebate

def active_debate_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.get(session=session)
    try:
        active_committee = Committee.objects.filter(session=session).get(name=active_debate.active_debate)
    except Committee.DoesNotExist:
        active_committee = None

    if active_committee is not None:
        active_debate_json = json.dumps({
            'active_debate_pk': active_committee.pk,
            'active_session_pk': session.pk
        })
    else:
        active_debate_json = json.dumps({
            'active_debate_pk': None,
            'active_session_pk': session.pk
        })
    return HttpResponse(active_debate_json, content_type='json')
