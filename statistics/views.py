import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

#Importing all models for statistics.
from .models import Session, Committee, Point, ContentPoint, Vote, SubTopic, ActiveDebate, ActiveRound

#Importing the forms too.
from .forms import PointForm, VoteForm, ActiveDebateForm, ActiveRoundForm

def home(request):
    #All the home page needs is a list of all sessions ordered by the start date. We create the list, then the context and finally render the template.
    latest_sessions_list = Session.objects.order_by('-session_start_date')[:20]
    context = {'latest_sessions_list': latest_sessions_list}
    return render(request, 'statistics/home.html', context)

def session(request, session_id):
    #The Session page uses static content and content that is constantly updated, the satic content is loaded with the view
    #and the updating content updates with the session api, defined further down.

    #The static data here is simply a list of the available committees (we can assume those don't change during live statistics)
    #and the name and data of the session itself.
    session_committee_list = Committee.objects.filter(session__id=session_id)[:30]
    session = Session.objects.get(pk=session_id)
    voting_enabled = session.session_voting_enabled
    context = {'session_committee_list': session_committee_list, 'session_id': session_id, 'session': session, 'voting_enabled': voting_enabled}
    return render(request, 'statistics/session.html', context)

def debate(request, session_id, committee_id):
    #Same for debates as for sessions, the only static content is the name and data of the committee and the session.
    #The rest of the point/voting data comes through the api that can constantly be updated.
    c = Committee.objects.get(pk=committee_id)
    s = Session.objects.get(pk=session_id)
    #The statistics_type will let us render different templates based on the statistics selected by the user.
    statistics_type = s.session_statistics
    print statistics_type

    #The voting enabled option lets us change the html content and js so that the voting is not displayed.
    voting_enabled = s.session_voting_enabled
    context = {'committee': c, 'session': s, 'statistics_type': statistics_type, 'voting_enabled': voting_enabled}

    if statistics_type == 'JF':
        return render(request, 'statistics/joint.html', context)
    elif statistics_type == 'SF':
        return render(request, 'statistics/joint.html', context)
    elif statistics_type == 'S':
        return render(request, 'statistics/statistics.html', context)
    elif statistics_type == 'C':
        return render(request, 'statistics/content.html', context)
    else:
        pass

def committee(request, session_id, committee_id):
    #The idea is not only to have a "debate page", where you can see how many points are made during the debate of a particular resolution,
    #but also for there to be a "committee page", where delegates can see how many points their
    #committee has made during each debate, what was the longest time between points etc.
    #This should be made in due time.
    pass

def point(request, session_id, committee_id):
    #The Point view handles the submission of points, both creating the form from the data given, validating the form,
    #and sending the user to the right place if the data submission was successful.

    #Here we get the active debate, get the committee of the active debate and get the active round no.
    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)
    active_round_no = ActiveRound.objects.get(session__pk=session_id).active_round

    #Get the subtopics of the active committee, and the loop through each one to create an array of subtopics.
    subtopics = SubTopic.objects.filter(committee=active_committee[0])
    subtopics_array = []
    for subtopic in subtopics:
        subtopics_array.append((subtopic.pk, subtopic.subtopic_text),)

    #Get the committee and session of the committee that wants to make a point.
    committee = Committee.objects.get(pk=committee_id)
    session = Session.objects.get(pk=session_id)

    #If the user is trying to submit data (method=POST), take a look at it
    if request.method == 'POST':
        #Print what the user is trying to submit for the sake of server logs.
        print request.POST

        #Create an instance of the form and populate it with data from the request.
        form = PointForm(subtopics_array, request.POST)

        #Check if the form is valid.
        if form.is_valid():
            #Create a point from the data submitted
            point = Point(session = Session.objects.filter(
                session_name=form.cleaned_data['session'])[0],
                committee_by=Committee.objects.filter(session__pk=session_id).filter(committee_name=form.cleaned_data['committee'])[0],
                active_debate=form.cleaned_data['debate'], active_round=form.cleaned_data['round_no'],
                point_type=form.cleaned_data['point_type']
                )
            #You need to first save the point before being able to add data to the ManyToManyField.
            point.save()
            #For each subtopic in the selected subtopics, add the subtopic to the saved points list of subtopics.
            for s in form.cleaned_data['subtopics']:
                st = SubTopic.objects.filter(pk=s)
                point.subtopics.add(st[0])

            #Once all that is done, send the user to the thank you page.
            return HttpResponseRedirect('/session/' + session_id + '/point/' + committee_id + '/thanks')

    else:
        #Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        form = PointForm(subtopics_array, {'session': session.session_name, 'committee': committee.committee_name, 'debate': active, 'round_no': active_round_no})


    context = {'debate': active, 'committee': committee, 'session': session, 'subtopics': subtopics, 'form': form}
    return render(request, 'statistics/point.html', context)

def vote(request, session_id, committee_id):
    #The Vote form is just as complex as the Point form, and is made in a very similar manner.

    #We get the current session and debate of the user, then get the active committee from the active debate.
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.get(pk=committee_id)
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)

    #If the user is trying to submit something:
    if request.method == 'POST':
        #Create an instance of the form and populate it with data from the request.
        form = VoteForm(request.POST)

        #If the data in the form is valid
        if form.is_valid():
            #Then make a vote from the data in the form.
            vote = Vote(session = Session.objects.filter(
                session_name=form.cleaned_data['session'])[0],
                committee_by=Committee.objects.filter(session__pk=session_id).filter(committee_name=form.cleaned_data['committee'])[0],
                active_debate=form.cleaned_data['debate'],
                in_favour=form.cleaned_data['in_favour'],
                against=form.cleaned_data['against'],
                abstentions=form.cleaned_data['abstentions'],
                absent=form.cleaned_data['absent']
                )
            #Save the vote to the database.
            vote.save()
            #Then send the user to the thank you page.
            return HttpResponseRedirect('/session/' + session_id + '/vote/' + committee_id + '/thanks')

    else:
        #Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        form = VoteForm({'session': session.session_name, 'committee': committee.committee_name, 'debate': active, 'in_favour': 0, 'against': 0, 'abstentions': 0, 'absent': 0})

    context = {'session': session, 'committee': committee, 'debate': active, 'form': form}
    return render(request, 'statistics/vote.html', context)

def thanks(request, session_id, committee_id):
    #A thanks page that is given a url for the user to submit something again. We construct the url here and then set it as the href="" on the button
    thanks_url = '/session/' + session_id + '/point/' + committee_id
    context = {'thanks_url': thanks_url}
    return render(request, 'statistics/thanks.html', context)

def vote_thanks(request, session_id, committee_id):
    #Same thing as the last thanks page, but with a url constructed for voting instead.
    thanks_url = '/session/' + session_id + '/vote/' + committee_id
    context = {'thanks_url': thanks_url}
    return render(request, 'statistics/thanks.html', context)

def manage(request, session_id):
    #The manage page contains 2 forms, one form for changing the active debate and one form for changing the active round.

    #First we set up our variables, we need the session, the active debate, the active round, the max rounds and a list of committees
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0]
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_round = ActiveRound.objects.filter(session__pk=session_id)[0].active_round
    active_round_entry = ActiveRound.objects.filter(session__pk=session_id)[0]
    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    #Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name),)
    #We need to make an array of each round with the round number and the place in the array
    #So we first make an array with the round numbers (1,2,3)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.session_max_rounds):
        n = i + 1
        max_rounds.append(n)
    #Then we make an array with the value and the position, so the form can accept the data.
    for r in max_rounds:
        max_rounds_array.append((r, r),)

    #If the user is trying to submit data
    if request.method == 'POST':
        #For server log purposes, print response
        print request.POST
        #if it's an active debate submission
        if 'active_debate' in request.POST:
            #Create an instance of the form and populate it with data from the request.
            debate_form = ActiveDebateForm(committees_array, request.POST)
            #If it's valid
            if debate_form.is_valid():
                #Get the committee that you want to change the active debate to and then set the active debate to be the new committees committee name.
                active_debate_committee = Committee.objects.get(pk=debate_form.cleaned_data['active_debate'])
                active_debate.active_debate = active_debate_committee.committee_name
                #Save the new active debate
                active_debate.save()
                #Send the user to the manage page
                return HttpResponseRedirect('/session/' + session_id + '/manage')
            else:
                print debate_form
            #You also have to create an empty/default instance of the "opposite" form, since we've got two on this page.
            round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})
        #otherwise if it's an active round submission
        elif 'active_round' in request.POST:
            #Create an instance of the form and populate it with data from the request.
            round_form = ActiveRoundForm(max_rounds_array, request.POST)
            #If the submission is valid
            if round_form.is_valid():
                #Change the active round entry to be the new round
                active_round_entry.active_round = round_form.cleaned_data['active_round']
                #Save the active round.
                active_round_entry.save()
                #Send the user back to the manage page
                return HttpResponseRedirect('/session/' + session_id + '/manage')
            debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})

    #Otherwise, give the User some nice new forms.
    else:
        debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})
        round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})

    context = {'session': session, 'committees': committees, 'active': active, 'active_round': active_round, 'debate_form': debate_form, 'round_form': round_form}
    return render(request, 'statistics/manage.html', context)

def session_api(request, session_id):
    #Since the graphs on the session page need to be able to livereload, we need to create
    #a custom "API" that outputs the neccesary JSON to keep the graph alive

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id)

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

def debate_api(request, session_id, committee_id):
    #The Debate API is very similar to the session API, but more complex due to more graphs and subtopics.

    #We get the active debate and active round
    active_debate = ActiveDebate.objects.filter(session__pk=session_id)
    active_round = ActiveRound.objects.filter(session__pk=session_id)
    active_round_no = active_round[0].active_round

    #We get the session, committee, and list of all committees.
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.filter(pk=committee_id)
    committees = Committee.objects.filter(session__id=session_id)

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
    committees = Committee.objects.filter(session__id=session_id)
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
    committees = Committee.objects.filter(session__id=session_id)

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

def content_api(request, session_id, committee_id, offset, count):
    #We need the committee to filter by active debate name.
    committee = Committee.objects.get(pk=committee_id)
    #For the 'offset' and 'count' arguments to work, we need to be able to tell the filter from which point and to which point to filter from.
    point_from = int(offset)
    point_to = int(offset) + int(count)
    #First we need all contentpoints from that session
    contentpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.committee_name).order_by('-pk')[point_from:point_to]
    #If there are no points, do nothing.
    if not contentpoints:
        pass

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

            #Create a single object with out data.
            thispoint = {
            'committee_by': committee_by,
            'point_type': point_type,
            'content': content,
            'pk': pk
            }

            contentpoint_list.append(thispoint)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'contentpoints': contentpoint_list
        })


    return HttpResponse(content_json, content_type='json')

def content_latest_api(request, session_id, committee_id, since):
    #We need the committee to filter by active debate name.
    committee = Committee.objects.get(pk=committee_id)
    #We need to get the contentpoints that have a pk greater than the "since" pk.
    contentpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.committee_name).filter(pk__gt=since).order_by('-pk')
    #If there are no points, do nothing.
    if not contentpoints:
        pass

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

            #Create a single object with out data.
            thispoint = {
            'committee_by': committee_by,
            'point_type': point_type,
            'content': content,
            'pk': pk
            }

            contentpoint_list.append(thispoint)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'contentpoints': contentpoint_list
        })


    return HttpResponse(content_json, content_type='json')
