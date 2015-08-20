import time
import json

from datetime import date
from datetime import datetime
from time import strftime

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages

#Importing all models for statistics.
from ..models import Session, Committee, Point, ContentPoint, Vote, SubTopic, ActiveDebate, ActiveRound

#Importing the forms too.
from ..forms import SessionForm,  SessionEditForm, PointForm, VoteForm, ContentForm, JointForm, ActiveDebateForm, ActiveRoundForm

def home(request):
    #All the home page needs is a list of all sessions ordered by the start date. We create the list, then the context and finally render the template.
    latest_sessions_list = Session.objects.filter(session_is_visible=True).order_by('-session_start_date')[:20]
    context = {'latest_sessions_list': latest_sessions_list}
    return render(request, 'statistics/home.html', context)




def create_session(request):
    #If the user is trying to create a session
    if request.method == 'POST':
        print request.POST
        #Fill an instance of a SessionForm with the request data.
        form = SessionForm(request.POST)

        if form.is_valid():
            print 'is valid'
            #We need to set up time varaibles for the start and end of sessions.
            #We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            #We need to turn the voting 'True' and 'False' strings into actual booleans.
            if form.cleaned_data['voting'] == 'True':
                voting = True
            else:
                voting = False

            #Creating a lowercase string with no spaces from the session name to use for usernames
            name = ''.join(form.cleaned_data['name'].split()).lower()

            #Creating the Admin user
            admin_user = User.objects.create_user(username = name + '_admin',
                email = form.cleaned_data['email'],
                password = form.cleaned_data['admin_password'])

            #Adding the admin user to the admin group.
            admin_group = Group.objects.get(name='SessionAdmin')
            admin_group.user_set.add(admin_user)

            #Creating the Submit user
            submit_user = User.objects.create_user(username = name,
                email = form.cleaned_data['email'],
                password = form.cleaned_data['submit_password'])

            #Adding the Submit user to the submit group.
            submit_group = Group.objects.get(name='SessionSubmit')
            submit_group.user_set.add(submit_user)

            #We need to create a session, active debate and active round. We also need to create 2 new users for the session.
            session = Session(session_name = form.cleaned_data['name'],
                session_description = form.cleaned_data['description'],
                session_picture = form.cleaned_data['picture'],
                session_email = form.cleaned_data['email'],
                session_country = form.cleaned_data['country'],
                session_start_date = start_date,
                session_end_date = end_date,
                session_statistics = form.cleaned_data['statistics'],
                session_color = form.cleaned_data['color'],
                session_rounds_enabled = True,
                session_subtopics_enabled = True,
                session_is_visible = False,
                session_voting_enabled = voting,
                session_max_rounds = form.cleaned_data['max_rounds'],
                session_admin_user = admin_user,
                session_submission_user = submit_user,
                )
            session.save()
            active_debate = ActiveDebate(session = session, active_debate = '')
            active_debate.save()
            active_round = ActiveRound(session = session, active_round = 1)
            active_round.save()

            #Once we've done all that, lets say thanks for all that hard work.
            return HttpResponseRedirect('/welcome/' + str(session.pk) + '/')
        else:
            print 'Wasnt valid'
            print form.errors
    else:
        #Otherwise, create a nice new form for the user.
        form = SessionForm()

    context = {'form': form}
    return render(request, 'statistics/session_create.html', context)

def welcome(request, session_id):
    session = Session.objects.get(pk=session_id)
    committees = Committee.objects.filter(session=session).order_by('committee_name')
    context = {'session': session, 'committees': committees}
    return render(request, 'statistics/welcome.html', context)

def edit(request, session_id):
    s = Session.objects.get(pk=session_id)
    # If the User is trying to edit the session
    if request.method == 'POST':
        #Fill an instance of the form with the request data.
        form = SessionEditForm(request.POST)
        #Check if the created form is a valid form.
        if form.is_valid():
            print 'is valid'
            #We need to set up time varaibles for the start and end of sessions.
            #We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            s.session_name = form.cleaned_data['name']
            s.session_description = form.cleaned_data['description']
            s.session_picture = form.cleaned_data['picture']
            s.session_email = form.cleaned_data['email']
            s.session_country = form.cleaned_data['country']
            s.session_start_date = start_date
            s.session_end_date = end_date
            s.session_statistics = form.cleaned_data['statistics']
            s.session_voting_enabled = form.cleaned_data['voting']
            s.session_max_rounds = form.cleaned_data['max_rounds']
            s.session_color = form.cleaned_data['color']
            s.session_is_visible = form.cleaned_data['is_visible']
            #Save the newly edited session
            s.save()

            messages.add_message(request, messages.SUCCESS, 'Session Updated')

    else:
        form = SessionEditForm({'name': s.session_name,
            'description': s.session_description,
            'email': s.session_email,
            'country': s.session_country,
            'picture': s.session_picture,
            'start_date': s.session_start_date.strftime("%Y-%m-%d"),
            'end_date': s.session_end_date.strftime("%Y-%m-%d"),
            'statistics': s.session_statistics,
            'voting': s.session_voting_enabled,
            'max_rounds': s.session_max_rounds,
            'color': s.session_color,
            'is_visible': s.session_is_visible})

    context = {'session': s, 'form': form}
    return render(request, 'statistics/session_edit.html', context)


def add(request, session_id):
    pass

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

    subtopics_array = []
    #Get the subtopics of the active committee, and the loop through each one to create an array of subtopics.
    if active_committee:
        subtopics = SubTopic.objects.filter(session_id=session_id).filter(committee=active_committee[0])
    else:
        subtopics = []
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
            point = Point(session = Session.objects.filter(session_name=form.cleaned_data['session'])[0],
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
    return render(request, 'statistics/point_form.html', context)

def content(request, session_id, committee_id):
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.get(pk=committee_id)
    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)
    if request.method == 'POST':
        print request.POST

        form = ContentForm(request.POST)
        if form.is_valid():
            contentpoint = ContentPoint(session = Session.objects.filter(session_name=form.cleaned_data['session'])[0],
                committee_by = Committee.objects.filter(session__pk=session_id).filter(committee_name=form.cleaned_data['committee'])[0],
                active_debate = form.cleaned_data['debate'],
                point_type = form.cleaned_data['point_type'],
                point_content = form.cleaned_data['content']
                )
            contentpoint.save()
            return HttpResponseRedirect('/session/' + session_id + '/content/' + committee_id + '/thanks')
    else:
        form = ContentForm({'session': session.session_name, 'committee': committee.committee_name, 'debate': active})

    context = {'debate': active, 'committee': committee, 'session': session, 'form': form}
    return render(request, 'statistics/content_form.html', context)

def joint(request, session_id, committee_id):
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.get(pk=committee_id)
    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)
    active_round_no = ActiveRound.objects.get(session__pk=session_id).active_round

    subtopics_array = []
    #Get the subtopics of the active committee, and the loop through each one to create an array of subtopics.
    if active_committee:
        subtopics = SubTopic.objects.filter(session_id=session_id).filter(committee=active_committee[0])
    else:
        subtopics = []
    for subtopic in subtopics:
        subtopics_array.append((subtopic.pk, subtopic.subtopic_text),)

    if request.method == 'POST':
        print request.POST

        form = JointForm(subtopics_array, request.POST)
        if form.is_valid():
            contentpoint = ContentPoint(session = Session.objects.filter(session_name=form.cleaned_data['session'])[0],
                committee_by = Committee.objects.filter(session__pk=session_id).filter(committee_name=form.cleaned_data['committee'])[0],
                active_debate = form.cleaned_data['debate'],
                point_type = form.cleaned_data['point_type'],
                point_content = form.cleaned_data['content']
                )
            contentpoint.save()
            #Create a point from the data submitted
            point = Point(session = Session.objects.filter(session_name=form.cleaned_data['session'])[0],
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
            return HttpResponseRedirect('/session/' + session_id + '/joint/' + committee_id + '/thanks')
    else:
        form = JointForm(subtopics_array, {'session': session.session_name, 'committee': committee.committee_name, 'debate': active, 'round_no': active_round_no})

    context = {'debate': active, 'committee': committee, 'session': session, 'subtopics': subtopics, 'form': form}
    return render(request, 'statistics/joint_form.html', context)

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
    return render(request, 'statistics/vote_form.html', context)

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

def content_thanks(request, session_id, committee_id):
    #Same thing as the last thanks page, but with a url constructed for contentpoints instead.
    thanks_url = '/session/' + session_id + '/content/' + committee_id
    context = {'thanks_url': thanks_url}
    return render(request, 'statistics/thanks.html', context)

def joint_thanks(request, session_id, committee_id):
    #Same thing as the last thanks page, but with a url constructed for contentpoints instead.
    thanks_url = '/session/' + session_id + '/joint/' + committee_id
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
