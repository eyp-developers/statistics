import json
from django.http import HttpResponse
from statisticscore.models import Session, Committee, Point, ContentPoint, Vote, \
                              ActiveDebate, ActiveRound


def debate_vote_api(request, session_id, committee_id):
    #The Debate API is very similar to the session API, but more complex due to more graphs and subtopics.

    #We get the active debate and active round
    active_debate = ActiveDebate.objects.filter(session__pk=session_id)
    active_round = ActiveRound.objects.filter(session__pk=session_id)
    active_round_no = active_round[0].active_round

    #We get the session, committee, and list of all committees.
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.filter(pk=committee_id)
    committees = Committee.objects.filter(session__id=session_id).order_by('name')

    #Making an array with the committee name.
    committee_array_name = []
    committee_array_name.append(committee[0].name)

    #Getting all votes
    votes = Vote.objects.filter(session__pk=session_id).filter(active_debate=committee[0].name)

    #Setting up more arrays for the voting graphs and zeroing values.
    committees_list = []
    committees_voted_list = []

    #Zeroing total values for the whole debate
    debate_in_favour = 0
    debate_against = 0
    debate_abstentions = 0
    debate_absent = 0
    total_counted = 0

    #Setting up arrays for committee specific votes
    committees_in_favour = []
    committees_against = []
    committees_abstentions = []
    committees_absent = []

    for v in votes:
        #For each vote, add the vote to the total
        debate_in_favour += v.in_favour
        debate_against += v.against
        debate_abstentions += v.abstentions
        debate_absent += v.absent
        total = v.in_favour + v.against + v.abstentions + v.absent
        total_counted += total

        #Then add the vote to the list of votes, for that specific committee
        committees_in_favour.append(v.in_favour)
        committees_against.append(v.against)
        committees_abstentions.append(v.abstentions)
        committees_absent.append(v.absent)

        committees_voted_list.append(v.committee_by.name)

    #Count the total committees and the ones that have voted for a nice counted/total fraction
    committees_count = len(committees)
    committees_voted = len(committees_voted_list)

    #Set up arrays and put the totals in the arrays for highcharts.
    debate_in_favour_array = []
    debate_against_array = []
    debate_abstentions_array = []
    debate_absent_array = []

    debate_in_favour_array.append(debate_in_favour)
    debate_against_array.append(debate_against)
    debate_abstentions_array.append(debate_abstentions)
    debate_absent_array.append(debate_absent)

    #Turn everything into JSON and render.
    debate_json = json.dumps({
    'name': committee_array_name,
    'committees_voted_list': committees_voted_list,
    'committees_count': committees_count,
    'committees_voted': committees_voted,
    'debate_in_favour': debate_in_favour_array,
    'debate_against': debate_against_array,
    'debate_abstentions': debate_abstentions_array,
    'debate_absent': debate_absent_array,
    'total_counted': total_counted,
    'committees_in_favour': committees_in_favour,
    'committees_against': committees_against,
    'committees_abstentions': committees_abstentions,
    'committees_absent': committees_absent,
    })
    return HttpResponse(debate_json, content_type='json')

def content_api(request, session_id, committee_id):
    #We need the committee to filter by active debate name.
    committee = Committee.objects.get(pk=committee_id)
    #For the 'offset' and 'count' arguments to work, we need to be able to tell the filter from which point and to which point to filter from.
    point_from = int(request.GET.get('offset'))
    point_to = int(request.GET.get('offset')) + int(request.GET.get('count'))
    #First we need all contentpoints from that session
    contentpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.name).order_by('-pk')[point_from:point_to]
    #We also need to count the points for the total
    totalpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.name).count()
    #If there are no points, do nothing.
    if not contentpoints:
        content_json = json.dumps({
        'contentpoints': 'No content'
        })

    #But if we could find points
    else:
        #Create an empty array to put the contentpoints in
        contentpoint_list = []
        #Loop through the avaliable contentpoints
        for p in contentpoints:
            #For each contentpoint, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            committee_by = p.committee_by.name
            point_type = p.point_type
            content = p.point_content
            pk = p.pk
            committee_color = p.committee_by.committee_color()
            committee_text_color = p.committee_by.committee_text_color()

            #Create a single object with out data.
            thispoint = {
            'committee_by': committee_by,
            'point_type': point_type,
            'contentpoint': content,
            'pk': pk,
            'committee_color': committee_color,
            'committee_text_color': committee_text_color
            }

            contentpoint_list.append(thispoint)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'contentpoints': contentpoint_list,
        'totalpoints': totalpoints
        })


    return HttpResponse(content_json, content_type='json')
