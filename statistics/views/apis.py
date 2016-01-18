import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from time import strftime
from decimal import *

#Importing all models for statistics.
from ..models import Session, Committee, Point, ContentPoint, RunningOrder, Vote, SubTopic, ActiveDebate, ActiveRound

from ..forms import PointEditForm, ContentEditForm, VoteEditForm, PredictEditForm, RunningOrderForm, DeleteDataForm

# #Importing the forms too.
# from ..forms import SessionForm,  SessionEditForm, PointForm, VoteForm, ContentForm, JointForm, ActiveDebateForm, ActiveRoundForm


def session_api(request, session_id):
    #Since the graphs on the session page need to be able to livereload, we need to create
    #a custom "API" that outputs the neccesary JSON to keep the graph alive

    session = Session.objects.get(pk=session_id)

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id).order_by('committee_name')

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
        first_point = all_points[0].timestamp
        latest_point = all_points.reverse()[0].timestamp
        time_diff = latest_point - first_point
        minutes = (time_diff.days * 1440) + (time_diff.seconds / 60)
        if total_points > 0:
            mpp = Decimal(minutes) / Decimal(total_points)
        else:
            mpp = 0
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
        'total_points': total_points,
        'type_point': type_point,
        'type_dr': type_dr,
        'mpp': round(mpp, 3),
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

    running_order = []
    if active_debate[0].active_debate == committee[0].committee_name:
        running = RunningOrder.objects.filter(session=session)
        if running:
            next_three = running.order_by('position')[:3]
            for point in next_three:
                running_order.append(point.committee_by.committee_name)


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
        'running_order': running_order
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
        'running_order': running_order
        })
    return HttpResponse(debate_json, content_type='json')

def session_vote_api(request, session_id):
    #This is for returning the specific vote data from the vote API for the voting chart on the session page.

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id).order_by('committee_name')
    #Then all the votes for that session
    votes = Vote.objects.filter(session_id=session_id)
    total_votes = 0
    total_in_favour = 0
    total_against = 0
    total_abstentions = 0
    total_absent = 0
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
        total_in_favour += debate_in_favour
        total_against += debate_against
        total_abstentions += debate_abstentions
        total_absent += debate_absent


    #Finally output the result as JSON
    total_votes = total_in_favour + total_against + total_abstentions + total_absent
    session_voting_json = json.dumps({
    'committees': committee_list,
    'in_favour': in_favour,
    'against': against,
    'abstentions': abstentions,
    'absent': absent,
    'total_votes': total_votes,
    'total_in_favour': total_in_favour,
    'total_against': total_against,
    'total_abstentions': total_abstentions,
    'total_absent': total_absent,
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
    elif json_datatype == 'predict':
        data = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).order_by('-pk')[point_from:point_to]
        total = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).count()


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
            elif request.GET.get('data_type') == 'point' or request.GET.get('data_type') == 'predict':
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
    if json_datatype == 'content':
        data = ContentPoint.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = ContentPoint.objects.filter(session_id=session_id).count()
    elif json_datatype == 'point':
        data = Point.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = Point.objects.filter(session_id=session_id).count()
    elif json_datatype == 'vote':
        data = Vote.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = Vote.objects.filter(session_id=session_id).count()
    elif json_datatype == 'predict':
        data = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        total = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).count()

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
            elif request.GET.get('data_type') == 'point' or request.GET.get('data_type') == 'predict':
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
        #If the user is trying to save/delete a peice of data.
        if request.POST.get('delete') == 'true':
            json_datatype = str(request.POST.get('data-type'))
            form = DeleteDataForm({'pk': int(request.POST.get('pk'))})
            if form.is_valid():
                if json_datatype == 'point':
                    d = Point.objects.get(pk=form.cleaned_data['pk'])
                if json_datatype == 'content':
                    d = ContentPoint.objects.get(pk=form.cleaned_data['pk'])
                if json_datatype == 'vote':
                    d = Vote.objects.get(pk=form.cleaned_data['pk'])
                d.delete()
                response_data = {}
                response_data['msg'] = 'Data deleted'

                response_json = json.dumps(response_data)

                return HttpResponse(response_json, content_type='json')

        else:
            if str(request.POST.get('data-type')) == 'predict':
                response_data = {}
                pk = int(request.POST.get('pk'))
                form = PredictEditForm({'pk': pk})
                subtopics = json.loads(request.POST.get('subtopics'))
                all_subtopics = json.loads(request.POST.get('all_subtopics'))

                if form.is_valid():
                    p = Point.objects.get(pk=form.cleaned_data['pk'])
                    p.subtopics.clear()

                    subtopics_array = []
                    for s in subtopics:
                        st = SubTopic.objects.get(pk=int(s.get('pk')))
                        p.subtopics.add(st)
                        subtopics_array.append(st.subtopic_text)

                    response_data['pk'] = p.pk
                    response_data['last_changed'] = p.timestamp.strftime("%H:%M")
                    response_data['by'] = p.committee_by.committee_name
                    response_data['debate'] = p.active_debate
                    response_data['round_no'] = p.active_round
                    response_data['point_type'] = p.point_type
                    response_data['subtopics'] = ', '.join(subtopics_array)
                    response_data['committee_color'] = p.committee_by.committee_color()
                    response_data['committee_text_color'] = p.committee_by.committee_text_color()

                    content_json = json.dumps(response_data)

                    return HttpResponse(content_json, content_type='json')
            else:
                #Get all our valiables according to what kind of data we're dealing with.
                response_data = {}
                json_datatype = str(request.POST.get('data-type'))
                session = int(request.POST.get('session'))
                pk = int(request.POST.get('pk'))
                committee = request.POST.get('committee')
                debate = request.POST.get('debate')
                if json_datatype == 'point':
                    round_no = int(request.POST.get('round_no'))
                    point_type = request.POST.get('point_type')
                    subtopics = json.loads(request.POST.get('subtopics'))
                    all_subtopics = json.loads(request.POST.get('all_subtopics'))

                    #Set up and instance of the Point Edit form.
                    form = PointEditForm({'pk': pk, 'session': session, 'committee': committee, 'debate': debate, 'round_no': round_no, 'point_type': point_type})

                    if form.is_valid():
                        print 'is valid!'
                        #If the form is valid, get the Point and update it with our values.
                        p = Point.objects.get(pk=form.cleaned_data['pk'])

                        committee_by = Committee.objects.filter(session_id=form.cleaned_data['session']).filter(committee_name=form.cleaned_data['committee'])[0]
                        p.committee_by = committee_by
                        p.active_debate = form.cleaned_data['debate']
                        p.active_round = form.cleaned_data['round_no']
                        p.point_type = form.cleaned_data['point_type']
                        p.save()
                        p.subtopics.clear()
                        subtopics_array = []
                        for s in subtopics:
                            st = SubTopic.objects.get(pk=int(s.get('pk')))
                            p.subtopics.add(st)
                            subtopics_array.append(st.subtopic_text)

                        response_data['pk'] = p.pk
                        response_data['last_changed'] = p.timestamp.strftime("%H:%M")
                        response_data['by'] = p.committee_by.committee_name
                        response_data['debate'] = p.active_debate
                        response_data['round_no'] = p.active_round
                        response_data['point_type'] = p.point_type
                        response_data['subtopics'] = ', '.join(subtopics_array)
                        response_data['committee_color'] = p.committee_by.committee_color()
                        response_data['committee_text_color'] = p.committee_by.committee_text_color()

                        content_json = json.dumps(response_data)

                        return HttpResponse(content_json, content_type='json')


                elif json_datatype == 'content':
                    point_type = request.POST.get('point_type')
                    content = request.POST.get('content')

                    form = ContentEditForm({'pk': pk, 'session': session, 'committee': committee, 'debate': debate, 'point_type': point_type, 'content': content})

                    if form.is_valid():
                        c = ContentPoint.objects.get(pk=form.cleaned_data['pk'])

                        committee_by = Committee.objects.filter(session_id=form.cleaned_data['session']).filter(committee_name=form.cleaned_data['committee'])[0]
                        c.committee_by = committee_by
                        c.active_debate = form.cleaned_data['debate']
                        c.point_type = form.cleaned_data['point_type']
                        c.point_content = form.cleaned_data['content']
                        c.save()

                        response_data['pk'] = c.pk
                        response_data['last_changed'] = c.timestamp.strftime("%H:%M")
                        response_data['by'] = c.committee_by.committee_name
                        response_data['debate'] = c.active_debate
                        response_data['point_type'] = c.point_type
                        response_data['content'] = c.point_content
                        response_data['committee_color'] = c.committee_by.committee_color()
                        response_data['committee_text_color'] = c.committee_by.committee_text_color()

                        content_json = json.dumps(response_data)

                        return HttpResponse(content_json, content_type='json')

                elif json_datatype == 'vote':
                    in_favour = request.POST.get('in_favour')
                    against = request.POST.get('against')
                    abstentions = request.POST.get('abstentions')
                    absent = request.POST.get('absent')

                    form = VoteEditForm({'pk': pk, 'session': session, 'committee': committee, 'debate': debate, 'in_favour': in_favour, 'against': against, 'abstentions': abstentions, 'absent': absent})

                    if form.is_valid():

                        v = Vote.objects.get(pk=form.cleaned_data['pk'])

                        committee_by = Committee.objects.filter(session_id=form.cleaned_data['session']).filter(committee_name=form.cleaned_data['committee'])[0]

                        v.committee_by = committee_by
                        v.active_debate = form.cleaned_data['debate']
                        v.in_favour = form.cleaned_data['in_favour']
                        v.against = form.cleaned_data['against']
                        v.abstentions = form.cleaned_data['abstentions']
                        v.absent = form.cleaned_data['absent']
                        v.save()

                        response_data['pk'] = v.pk
                        response_data['last_changed'] = v.timestamp.strftime("%H:%M")
                        response_data['by'] = v.committee_by.committee_name
                        response_data['debate'] = v.active_debate
                        response_data['in_favour'] = v.in_favour
                        response_data['against'] = v.against
                        response_data['abstentions'] = v.abstentions
                        response_data['absent'] = v.absent
                        response_data['committee_color'] = v.committee_by.committee_color()
                        response_data['committee_text_color'] = v.committee_by.committee_text_color()

                        content_json = json.dumps(response_data)

                        return HttpResponse(content_json, content_type='json')

        return HttpResponse(
            json.dumps({'opps': 'something went wrong'}),
            content_type='json'
        )
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
            active_committee = Committee.objects.filter(session=data.session).filter(committee_name=data.active_debate)[0]
            all_subtopics = SubTopic.objects.filter(committee=active_committee)
            all_subtopics_array = []
            for subtopic in all_subtopics:
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.subtopic_text
                }
                all_subtopics_array.append(this_subtopic)
            thisdata['all_subtopics'] = all_subtopics_array
        elif json_datatype == 'predict':
            data = Point.objects.get(pk=pk)
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
            active_committee = Committee.objects.filter(session=data.session).filter(committee_name=data.active_debate)[0]
            all_subtopics = SubTopic.objects.filter(committee=active_committee)
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

def position(data, session, position=0):
    order = RunningOrder.objects.filter(session=session).order_by('position')
    count = order.count()
    if count == 0:
        return 1
    else:
        if data == 'P':
            return count + 1;
        elif data == 'DR':
            for point in order:
                point.position += 1
                point.save()
            return 1
        elif data == 'R':
            for point in order:
                point.position += -1
                point.save()
        elif data == 'up':
            if position > 1:
                point = order.get(position=position)
                above = order.get(position=(position-1))
                point.position += -1
                above.position += 1
                point.save()
                above.save()
        elif data == 'down':
            if position < RunningOrder.objects.filter(session=session).order_by('-position')[0].position:
                point = order.get(position=position)
                below = order.get(position=(position+1))
                point.position += 1
                below.position += -1
                point.save()
                below.save()
        else:
            for point in order:
                if point.position > data:
                    point.position += -1
                    point.save()

def runningorder_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.get(session=session).active_debate
    active_round = ActiveRound.objects.get(session=session).active_round
    thisdata = {}
    if request.method == 'POST':
        if request.POST.get('action') == 'R':
            if Point.objects.filter(session=session).count() < 0:
                dr_subtopics = Point.objects.filter(session=session).order_by('-pk')[0].subtopics.all()
            else:
                dr_subtopics = []
            point = RunningOrder.objects.filter(session=session).order_by('position')[0]
            newpoint = Point(session = session,
                committee_by = point.committee_by,
                active_debate = active_debate,
                active_round = active_round,
                point_type = point.point_type
                )
            newpoint.save()
            if point.point_type == 'P':
                for s in point.committee_by.next_subtopics.all():
                    newpoint.subtopics.add(s)
            else:
                for s in dr_subtopics:
                    newpoint.subtopics.add(s)
            point.delete()
            position('R', session)

        elif request.POST.get('action') == 'U':
            point = Point.objects.filter(session=session).order_by('-pk')[0]
            r = RunningOrder(
                session = session,
                position = position('DR', session),
                committee_by = point.committee_by,
                point_type = point.point_type
            )
            r.save()
            point.delete()
        elif request.POST.get('action') == 'C':
            queue = RunningOrder.objects.filter(session=session)
            for point in queue:
                point.delete()
        elif request.POST.get('action') == 'delete':
            pos = int(request.POST.get('position'))
            point = RunningOrder.objects.filter(session=session).filter(position=pos)
            point.delete()
            position(pos, session)
        elif request.POST.get('action') == 'move':
            position(str(request.POST.get('direction')), session, int(request.POST.get('position')))
        else:
            form = RunningOrderForm({'by': int(request.POST.get('by')), 'point_type': str(request.POST.get('type'))})
            if form.is_valid():
                r = RunningOrder(session=session,
                    position=position(form.cleaned_data['point_type'], session),
                    committee_by=Committee.objects.get(pk=form.cleaned_data['by']),
                    point_type=form.cleaned_data['point_type']
                    )
                r.save()
    else:
        committees = Committee.objects.filter(session=session)
        session_points = Point.objects.filter(session=session)
        debate_points = session_points.filter(active_debate=active_debate)
        committees_array = []
        for committee in committees:
            committee_session_points = session_points.filter(committee_by=committee).count()
            committee_debate_points = debate_points.filter(committee_by=committee).count()
            if (debate_points.count() != 0) & (session_points.count() != 0):
                height = Decimal(75)+(Decimal(25)-(Decimal(15)*(Decimal(committee_debate_points)/Decimal(debate_points.count())))+(Decimal(10)*(Decimal(committee_session_points)/Decimal(session_points.count()))))
            else:
                height = 75
            subtopics_next_array = []
            for subtopic in committee.next_subtopics.all():
                thissubtopic = {
                'subtopic': subtopic.subtopic_text,
                'color': subtopic.subtopic_color(),
                'text_color': subtopic.subtopic_text_color()
                }
                subtopics_next_array.append(thissubtopic)
            thiscommittee = {
                'pk': committee.pk,
                'session_total': committee_session_points,
                'debate_total': committee_debate_points,
                'next_subtopics': subtopics_next_array,
                'height': round(height, 4)
            }
            committees_array.append(thiscommittee)
        thisdata['committees'] = committees_array
        last_three = session_points.order_by('-pk')[0:3]
        backlog_array = []
        backlog_position = -1
        for point in last_three:
            point_subtopics = []
            for subtopic in point.subtopics.all():
                thissubtopic = {
                'subtopic': subtopic.subtopic_text,
                'color': subtopic.subtopic_color(),
                'text_color': subtopic.subtopic_text_color()
                }
                point_subtopics.append(thissubtopic)
            thispoint = {
                'position': backlog_position,
                'by': point.committee_by.committee_name,
                'on': point.active_debate,
                'round': point.active_round,
                'type': point.point_type,
                'subtopics': point_subtopics
            }
            backlog_position += -1
            backlog_array.append(thispoint)
        thisdata['backlog'] = backlog_array

        queue = RunningOrder.objects.filter(session=session).order_by('position')
        queue_array = []
        for point in queue:
            point_subtopics = []
            if point.point_type == 'P':
                for subtopic in point.committee_by.next_subtopics.all():
                    thissubtopic = {
                    'subtopic': subtopic.subtopic_text,
                    'color': subtopic.subtopic_color(),
                    'text_color': subtopic.subtopic_text_color()
                    }
                    point_subtopics.append(thissubtopic)
            else:
                for subtopic in last_three[0].subtopics.all():
                    thissubtopic = {
                    'subtopic': subtopic.subtopic_text,
                    'color': subtopic.subtopic_color(),
                    'text_color': subtopic.subtopic_text_color()
                    }
                    point_subtopics.append(thissubtopic)

            thispoint = {
                'position': point.position,
                'by': point.committee_by.committee_name,
                'on': active_debate,
                'round': active_round,
                'type': point.point_type,
                'subtopics': point_subtopics
            }
            queue_array.append(thispoint)
        thisdata['queue'] = queue_array


    content_json = json.dumps(thisdata)

    return HttpResponse(content_json, content_type='json')
