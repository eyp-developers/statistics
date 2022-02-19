import json
from django.http import HttpResponse
from statisticscore.models import Session, Committee, SubTopic

def committees_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    #Let's get the committee in question
    committee = Committee.objects.get(pk=request.GET.get('pk'))
    #Then lets get the subtopics for that committee
    committee_subtopics = SubTopic.objects.filter(committee=committee)
    #We need to make a nice array of the subtopics
    committee_subtopics_array = []
    for subtopic in committee_subtopics:
        this_subtopic = {
        'pk': subtopic.pk,
        'subtopic': subtopic.text
        }
        committee_subtopics_array.append(this_subtopic)
    #Then lets make a JSON object with the data from that committee
    thiscommittee = json.dumps({
    'pk': committee.pk,
    'name': committee.name,
    'topic_text': committee.topic_text,
    'subtopics': committee_subtopics_array
    })

    return HttpResponse(thiscommittee, content_type='json')
