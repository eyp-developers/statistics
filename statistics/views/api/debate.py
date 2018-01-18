import json
from django.http import HttpResponse
from statistics.models import Session, Committee, Point, RunningOrder, Vote, \
                              SubTopic, ActiveDebate, ActiveRound

def debate_api(request, session_id, committee_id):
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

    #Getting all points (both Point and DR), just points, just DRs and all votes
    all_points = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].name)
    points = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].name).filter(point_type='P')
    drs = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].name).filter(point_type='DR')

    #If the points couldn't be retreived (If there were no points made yet) then don't do anything
    if not all_points:
        pass
    #But if there were points available
    else:
        #We want the name of the committee that made the last point.
        latest_point_name = all_points.order_by('-timestamp')[0].committee_by.name
        #Then we want the subtopics that that point addressed.
        latest_point_subtopics = all_points.order_by('-timestamp')[0].subtopics.all()
        latest_point_subtopics_array = []

        #For each sutopic the latest point addressed, append the text of the subtopic to the array
        for s in latest_point_subtopics:
            latest_point_subtopics_array.append(s.text)

        #Now we're moving away from just the latest point, we want all subtopics connected to the committee in question.
        subtopics = SubTopic.objects.filter(session__pk=session_id).filter(committee__name=committee[0].name)
        #Get the maximum number of allowed rounds for the session in question.
        no_rounds = list(range(session.max_rounds))

        #Set up the needed arrays
        subtopics_array = []
        subtopic_points_array = []

        #For each available subtopic, append the subtopic text to the subtopics array
        for s in subtopics:
            subtopics_array.append(s.text)

        #For each round available
        for r in no_rounds:
            #The round numer should be the round + 1
            r_n = r + 1
            #Create an array for that round.
            round_array = []
            #Filter all the points by that round number
            round_points = all_points.filter(active_round=r_n)
            #For each subtopic
            for s in subtopics:
                #Append the number of points made on that subtopic to the round array
                round_array.append(round_points.filter(subtopics=s).count())

            #Append the newly made array to the subtopic points array, this means that the subtopic points array
            #will be an array containing an array for each available round, filled with a value for the number of points
            #made on each subtopic.
            subtopic_points_array.append(round_array)

        #A simple boolean for whether or not the debate in question is the active debate.
        is_active = active_debate[0].active_debate == committee[0].name

    #Setting up more arrays for the voting graphs and zeroing values.
    committees_list = []

    points_total = 0
    type_point = 0
    type_dr = 0

    points_made = []
    drs_made = []

    for c in committees:
        com_name = c.name
        p = points.filter(committee_by__name=com_name).count()
        d = drs.filter(committee_by__name=com_name).count()

        points_total += p
        points_total += d
        type_point += p
        type_dr += d

        committees_list.append(com_name)
        points_made.append(p)
        drs_made.append(d)

    running_order = []
    if active_debate[0].active_debate == committee[0].name:
        running = RunningOrder.objects.filter(session=session)
        if running:
            next_three = running.order_by('position')[:3]
            for point in next_three:
                running_order.append(point.committee_by.name)


    if not all_points:
        debate_json = json.dumps({
        'name': committee_array_name,
        'is_active': 'false',
        'committees_list': committees_list,
        'points_total': points_total,
        'type_point': type_point,
        'type_dr': type_dr,
        'points_made': [],
        'drs_made': drs_made,
        'latest_point_name': '',
        'latest_point_subtopics': '',
        'subtopics': [],
        'subtopic_points': [],
        'running_order': running_order
        })
    else:
        debate_json = json.dumps({
        'name': committee_array_name,
        'is_active': is_active,
        'committees_list': committees_list,
        'points_total': points_total,
        'type_point': type_point,
        'type_dr': type_dr,
        'points_made': points_made,
        'drs_made': drs_made,
        'latest_point_name': latest_point_name,
        'latest_point_subtopics': latest_point_subtopics_array,
        'subtopics': subtopics_array,
        'subtopic_points': subtopic_points_array,
        'running_order': running_order
        })
    return HttpResponse(debate_json, content_type='json')
