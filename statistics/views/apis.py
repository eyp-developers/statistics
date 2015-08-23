import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from time import strftime

#Importing all models for statistics.
from ..models import Session, Committee, Point, ContentPoint, Vote, SubTopic, ActiveDebate, ActiveRound

# #Importing the forms too.
# from ..forms import SessionForm,  SessionEditForm, PointForm, VoteForm, ContentForm, JointForm, ActiveDebateForm, ActiveRoundForm


def session_api(request, session_id):
    #Since the graphs on the session page need to be able to livereload, we need to create
    #a custom "API" that outputs the neccesary JSON to keep the graph alive

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id).order_by('committee_name')

    #Then we need all the available points, direct responses and votes
    points = Point.objects.filter(session_id=session_id).filter(point_type='P')
    drs = Point.objects.filter(session_id=session_id).filter(point_type='DR')

    #Then we need a list of each of them.
    committee_list = []
    points_list = []
    drs_list = []

    #For each committee,
    for committee in committees:
        #Let c be the name
        c = committee.committee_name
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
    })
    return HttpResponse(session_json, content_type='json')

def active_debate_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.get(session=session)
    active_committee = Committee.objects.filter(committee_name=active_debate.active_debate)[0]

    active_debate_json = json.dumps({
    'active_debate_pk': active_committee.pk,
    'active_session_pk': session.pk
    })
    return HttpResponse(active_debate_json, content_type='json')

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
        'subtopic': subtopic.subtopic_text
        }
        committee_subtopics_array.append(this_subtopic)
    #Then lets make a JSON object with the data from that committee
    thiscommittee = json.dumps({
    'pk': committee.pk,
    'name': committee.committee_name,
    'topic': committee.committee_topic,
    'subtopics': committee_subtopics_array
    })

    return HttpResponse(thiscommittee, content_type='json')

def debate_api(request, session_id, committee_id):
    #The Debate API is very similar to the session API, but more complex due to more graphs and subtopics.

    #We get the active debate and active round
    active_debate = ActiveDebate.objects.filter(session__pk=session_id)
    active_round = ActiveRound.objects.filter(session__pk=session_id)
    active_round_no = active_round[0].active_round

    #We get the session, committee, and list of all committees.
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.filter(pk=committee_id)
    committees = Committee.objects.filter(session__id=session_id).order_by('committee_name')

    #Making an array with the committee name.
    committee_array_name = []
    committee_array_name.append(committee[0].committee_name)

    #Getting all points (both Point and DR), just points, just DRs and all votes
    all_points = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name)
    points = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name).filter(point_type='P')
    drs = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name).filter(point_type='DR')

    #If the points couldn't be retreived (If there were no points made yet) then don't do anything
    if not all_points:
        pass
    #But if there were points available
    else:
        #We want the name of the committee that made the last point.
        latest_point_name = all_points.order_by('-timestamp')[0].committee_by.committee_name
        #Then we want the subtopics that that point addressed.
        latest_point_subtopics = all_points.order_by('-timestamp')[0].subtopics.all()
        latest_point_subtopics_array = []

        #For each sutopic the latest point addressed, append the text of the subtopic to the array
        for s in latest_point_subtopics:
            latest_point_subtopics_array.append(s.subtopic_text)

        #Now we're moving away from just the latest point, we want all subtopics connected to the committee in question.
        subtopics = SubTopic.objects.filter(session__pk=session_id).filter(committee__committee_name=committee[0].committee_name)
        #Get the maximum number of allowed rounds for the session in question.
        no_rounds = range(session.session_max_rounds)

        #Set up the needed arrays
        subtopics_array = []
        subtopic_points_array = []

        #For each available subtopic, append the subtopic text to the subtopics array
        for s in subtopics:
            subtopics_array.append(s.subtopic_text)

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
        is_active = active_debate[0].active_debate == committee[0].committee_name

    #Setting up more arrays for the voting graphs and zeroing values.
    committees_list = []

    points_total = 0
    type_point = 0
    type_dr = 0

    points_made = []
    drs_made = []

    for c in committees:
        com_name = c.committee_name
        p = points.filter(committee_by__committee_name=com_name).count()
        d = drs.filter(committee_by__committee_name=com_name).count()

        points_total += p
        points_total += d
        type_point += p
        type_dr += d

        committees_list.append(com_name)
        points_made.append(p)
        drs_made.append(d)

    if not all_points:
        debate_json = json.dumps({
        'committee_name': committee_array_name,
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
        })
    else:
        debate_json = json.dumps({
        'committee_name': committee_array_name,
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
        })
    return HttpResponse(debate_json, content_type='json')

def session_vote_api(request, session_id):
    #This is for returning the specific vote data from the vote API for the voting chart on the session page.

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id).order_by('committee_name')
    #Then all the votes for that session
    votes = Vote.objects.filter(session_id=session_id)
    #Then a list to add committee names to
    committee_list = []

    #And lists for different vote types
    in_favour = []
    against = []
    abstentions = []
    absent = []

    #For each committee,
    for committee in committees:
        #Let c be the name
        c = committee.committee_name

        #Append each newly made variable to our nice lists.
        committee_list.append(c)

        #Set the counter for each vote type to 0
        debate_in_favour = 0
        debate_against = 0
        debate_abstentions = 0
        debate_absent = 0

        #Filter votes by the current committee
        v = votes.filter(active_debate=committee)

        #For each vote in the new list of votes
        for vc in v:
            #Add that votes count to the total count
            debate_in_favour += vc.in_favour
            debate_against += vc.against
            debate_abstentions += vc.abstentions
            debate_absent += vc.absent

        #Then, append the totals to the full list.
        in_favour.append(debate_in_favour)
        against.append(debate_against)
        abstentions.append(debate_abstentions)
        absent.append(debate_absent)

    #Finally output the result as JSON
    session_voting_json = json.dumps({
    'committees': committee_list,
    'in_favour': in_favour,
    'against': against,
    'abstentions': abstentions,
    'absent': absent
    })
    return HttpResponse(session_voting_json, content_type='json')

def debate_vote_api(request, session_id, committee_id):
    #The Debate API is very similar to the session API, but more complex due to more graphs and subtopics.

    #We get the active debate and active round
    active_debate = ActiveDebate.objects.filter(session__pk=session_id)
    active_round = ActiveRound.objects.filter(session__pk=session_id)
    active_round_no = active_round[0].active_round

    #We get the session, committee, and list of all committees.
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.filter(pk=committee_id)
    committees = Committee.objects.filter(session__id=session_id).order_by('committee_name')

    #Making an array with the committee name.
    committee_array_name = []
    committee_array_name.append(committee[0].committee_name)

    #Getting all votes
    votes = Vote.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name)

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

        committees_voted_list.append(v.committee_by.committee_name)

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
    'committee_name': committee_array_name,
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
    contentpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.committee_name).order_by('-pk')[point_from:point_to]
    #We also need to count the points for the total
    totalpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.committee_name).count()
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
            committee_by = p.committee_by.committee_name
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

def content_latest_api(request, session_id, committee_id):
    #We need the committee to filter by active debate name.
    committee = Committee.objects.get(pk=committee_id)
    #We need to get the contentpoints that have a pk greater than the "since" pk.
    contentpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.committee_name).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
    #We also need to count the points for the total
    totalpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.committee_name).count()
    #Create an empty array to put the contentpoints in
    contentpoint_list = []
    #If there are no points, do nothing.
    if not contentpoints:
        #Create a single object with out data.
        thispoint = {
        'pk': request.GET.get('pk')
        }

        contentpoint_list.append(thispoint)

        content_json = json.dumps({
        'contentpoints': contentpoint_list,
        'totalpoints': totalpoints
        })

    #But if we could find points
    else:
        #Loop through the avaliable contentpoints
        for p in contentpoints:
            #For each contentpoint, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            committee_by = p.committee_by.committee_name
            point_type = p.point_type
            content = p.point_content
            pk = p.pk
            committee_color = p.committee_by.committee_color()
            committee_text_color = p.committee_by.committee_text_color()

            #Create a single object with our data.
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
        'contentpoints': contentpoint_list
        })


    return HttpResponse(content_json, content_type='json')

def data_api(request, session_id):
    #For the 'offset' and 'count' arguments to work, we need to be able to tell the filter from which point and to which point to filter from.
    point_from = int(request.GET.get('offset'))
    point_to = int(request.GET.get('offset')) + int(request.GET.get('count'))
    #First we need all datapoints from that session
    json_datatype = str(request.GET.get('data_type'))
    print json_datatype
    if json_datatype == 'content':
        print 'yup, content'
        data = ContentPoint.objects.filter(session_id=session_id).order_by('-pk')[point_from:point_to]
        #We also need to count the amount of data points for the total
        total = ContentPoint.objects.filter(session_id=session_id).count()
    elif json_datatype == 'point':
        print 'yup, point'
        data = Point.objects.filter(session_id=session_id).order_by('-pk')[point_from:point_to]
        #We also need to count the amount of data points for the total
        total = Point.objects.filter(session_id=session_id).count()
    elif json_datatype == 'vote':
        print 'yup, vote'
        data = Vote.objects.filter(session_id=session_id).order_by('-pk')[point_from:point_to]
        #We also need to count the amount of data points for the total
        total = Vote.objects.filter(session_id=session_id).count()


    #If there is no data, do nothing.
    if not data:
        content_json = json.dumps({
        'data': 'No data'
        })

    #But if we could find data
    else:
        #Create an empty array to put the data in
        data_list = []
        #Loop through the avaliable data
        for d in data:
            #For each data point, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            thisdata = {}
            thisdata['pk'] = d.pk
            thisdata['last_changed'] = d.timestamp.strftime("%H:%M")
            thisdata['committee_by'] = d.committee_by.committee_name
            thisdata['active_debate'] = d.active_debate
            thisdata['committee_color'] = d.committee_by.committee_color()
            thisdata['committee_text_color'] = d.committee_by.committee_text_color()

            #For the different kinds of data points, we need to get different types of data.
            if request.GET.get('data_type') == 'content':
                thisdata['point_type'] = d.point_type
                thisdata['content'] = d.point_content
            elif request.GET.get('data_type') == 'point':
                thisdata['point_type'] = d.point_type
                thisdata['round_no'] = d.active_round
                subtopics_array = []
                for subtopic in d.subtopics.all():
                    subtopics_array.append(subtopic.subtopic_text)
                thisdata['subtopics'] = ', '.join(subtopics_array)
            elif request.GET.get('data_type') == 'vote':
                thisdata['in_favour'] = d.in_favour
                thisdata['against'] = d.against
                thisdata['abstentions'] = d.abstentions
                thisdata['absent'] = d.absent

            data_list.append(thisdata)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'datapoints': data_list,
        'totaldata': total
        })


    return HttpResponse(content_json, content_type='json')

def data_latest_api(request, session_id):
    #First we need all datapoints from that session that have a greater pk than *
    json_datatype = str(request.GET.get('data_type'))
    print json_datatype
    if json_datatype == 'content':
        print 'yup, content'
        data = ContentPoint.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = ContentPoint.objects.filter(session_id=session_id).count()
    elif json_datatype == 'point':
        print 'yup, point'
        data = Point.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = Point.objects.filter(session_id=session_id).count()
    elif json_datatype == 'vote':
        print 'yup, vote'
        data = Vote.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = Vote.objects.filter(session_id=session_id).count()

    #Create an empty array to put the contentpoints in
    data_list = []
    #If there are no points, do nothing.
    if not data:
        #Create a single object with out data.
        thisdata = {
        'pk': request.GET.get('pk')
        }

        data_list.append(thisdata)

        content_json = json.dumps({
        'datapoints': data_list,
        'totaldata': total
        })

    #But if we could find points
    else:
        #Loop through the avaliable contentpoints
        for d in data:
            #For each data point, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            thisdata = {}
            thisdata['pk'] = d.pk
            thisdata['last_changed'] = d.timestamp.strftime("%H:%M")
            thisdata['committee_by'] = d.committee_by.committee_name
            thisdata['active_debate'] = d.active_debate
            thisdata['committee_color'] = d.committee_by.committee_color()
            thisdata['committee_text_color'] = d.committee_by.committee_text_color()

            #For the different kinds of data points, we need to get different types of data.
            if request.GET.get('data_type') == 'content':
                thisdata['point_type'] = d.point_type
                thisdata['content'] = d.point_content
            elif request.GET.get('data_type') == 'point':
                thisdata['point_type'] = d.point_type
                thisdata['round_no'] = d.active_round
                subtopics_array = []
                for subtopic in d.subtopics.all():
                    subtopics_array.append(subtopic.subtopic_text)
                thisdata['subtopics'] = ', '.join(subtopics_array)
            elif request.GET.get('data_type') == 'vote':
                thisdata['in_favour'] = d.in_favour
                thisdata['against'] = d.against
                thisdata['abstentions'] = d.abstentions
                thisdata['absent'] = d.absent

            data_list.append(thisdata)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'datapoints': data_list,
        'totaldata': total
        })


    return HttpResponse(content_json, content_type='json')

def data_pk_api(request):
    if request.method == 'POST':
        #If the user is trying to save a peice of data.
        pass
    else:
        json_datatype = str(request.GET.get('data_type'))
        pk = int(request.GET.get('pk'))
        thisdata = {}
        if json_datatype == 'content':
            data = ContentPoint.objects.get(pk=pk)
            thisdata['point_type'] = data.point_type
            thisdata['content'] = data.point_content
        elif json_datatype == 'point':
            data = Point.objects.get(pk=pk)
            thisdata['point_type'] = data.point_type
            thisdata['round_no'] = data.active_round
            #Getting the subtopics for a point
            subtopics_array = []
            for subtopic in data.subtopics.all():
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.subtopic_text
                }
                subtopics_array.append(this_subtopic)
            thisdata['subtopics'] = subtopics_array
            #Getting all the subtopics avaliable for a certain point
            all_subtopics = SubTopic.objects.filter(committee=data.committee_by)
            all_subtopics_array = []
            for subtopic in all_subtopics:
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.subtopic_text
                }
                all_subtopics_array.append(this_subtopic)
            thisdata['all_subtopics'] = all_subtopics_array
        elif json_datatype == 'vote':
            data = Vote.objects.get(pk=pk)
            thisdata['in_favour'] = data.in_favour
            thisdata['against'] = data.against
            thisdata['abstentions'] = data.abstentions
            thisdata['absent'] = data.absent

        thisdata['pk'] = data.pk
        thisdata['committee_by'] = data.committee_by.committee_name
        thisdata['active_debate'] = data.active_debate

        content_json = json.dumps(thisdata)

        return HttpResponse(content_json, content_type='json')
