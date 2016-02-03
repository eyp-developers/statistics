import time
import json

from datetime import date
from datetime import datetime
from time import strftime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Importing all models for statistics.
from ..models import Session, Committee, Point, ContentPoint, RunningOrder, Vote, SubTopic, ActiveDebate, ActiveRound, Gender

# Importing the forms too.
from ..forms import SessionForm, SessionEditForm, CommitteeForm, PointForm, PointEditForm, VoteForm, VoteEditForm,\
    ContentForm, ContentEditForm, JointForm, ActiveDebateForm, ActiveRoundForm, PredictForm, PredictEditForm, GenderForm


# This is a central function. It replaces 'render' in cases where the user has to be authorized to view the page, not just authenticated.
def check_authorization_and_render(request, template, context, session, admin_only=True):
    if admin_only:  # This also refers to the session admin user AND any superuser
        if request.user == session.session_admin_user or request.user.is_superuser:
            return render(request, template, context)
        else:
            messages.add_message(request, messages.ERROR,
                                 'You are not authorized to view this page. You need to log in as the ' + session.session_name + 'admin.')
            return HttpResponseRedirect(reverse('statistics:login'))
    else:
        if request.user == session.session_admin_user or request.user == session.session_submission_user or request.user.is_superuser:
            return render(request, template, context)
        else:
            messages.add_message(request, messages.ERROR,
                                 'You are not authorized to view this page. You need to log in as the ' + session.session_name + 'admin.')
            return HttpResponseRedirect(reverse('statistics:login'))


#################

# This view should be renamed to overview in accordance to what the user sees
@login_required(login_url='/login/')
def welcome(request, session_id):
    session = Session.objects.get(pk=session_id)
    committees = Committee.objects.filter(session=session).order_by('committee_name')
    context = {'session': session, 'committees': committees}

    return check_authorization_and_render(request, 'statistics/welcome.html', context, session)


#################


@login_required(login_url='/login/')
def edit(request, session_id):
    s = Session.objects.get(pk=session_id)
    # If the User is trying to edit the session
    if request.method == 'POST':
        # Fill an instance of the form with the request data.
        form = SessionEditForm(request.POST, request.FILES)
        # Check if the created form is a valid form.
        if form.is_valid():
            print 'is valid'
            # We need to set up time varaibles for the start and end of sessions.
            # We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            s.session_name = form.cleaned_data['name']
            s.session_description = form.cleaned_data['description']
            if form.cleaned_data['picture'] is not None:
                s.session_picture = form.cleaned_data['picture']
            s.session_resolution_link = form.cleaned_data['resolution']
            s.session_website_link = form.cleaned_data['website']
            s.session_facebook_link = form.cleaned_data['facebook']
            s.session_twitter_link = form.cleaned_data['twitter']
            s.session_email = form.cleaned_data['email']
            s.session_country = form.cleaned_data['country']
            s.session_start_date = start_date
            s.session_end_date = end_date
            s.session_statistics = form.cleaned_data['statistics']
            s.session_voting_enabled = form.cleaned_data['voting_enabled']
            s.session_gender_enabled = form.cleaned_data['gender_statistics']
            s.session_max_rounds = form.cleaned_data['max_rounds']
            s.session_is_visible = form.cleaned_data['is_visible']
            s.session_has_technical_problems = form.cleaned_data['technical_problems']
            if form.cleaned_data['number_female_participants'] is not None:
                s.gender_number_female = form.cleaned_data['number_female_participants']
            if form.cleaned_data['number_male_participants'] is not None:
                s.gender_number_male = form.cleaned_data['number_male_participants']
            if form.cleaned_data['number_other_participants'] is not None:
                s.gender_number_other = form.cleaned_data['number_other_participants']
            # Save the newly edited session
            s.save()

            messages.add_message(request, messages.SUCCESS, 'Session Updated')
            return HttpResponseRedirect(reverse('statistics:edit', args=[session_id]))

    else:
        form = SessionEditForm({'name': s.session_name,
                                'description': s.session_description,
                                'email': s.session_email,
                                'country': s.session_country,
                                'picture': s.session_picture.url,
                                'website': s.session_website_link,
                                'facebook': s.session_facebook_link,
                                'twitter': s.session_twitter_link,
                                'resolution': s.session_resolution_link,
                                'start_date': s.session_start_date.strftime("%Y-%m-%d"),
                                'end_date': s.session_end_date.strftime("%Y-%m-%d"),
                                'statistics': s.session_statistics,
                                'voting_enabled': s.session_voting_enabled,
                                'gender_statistics': s.session_gender_enabled,
                                'max_rounds': s.session_max_rounds,
                                'is_visible': s.session_is_visible,
                                'technical_problems': s.session_has_technical_problems})

    context = {'session': s, 'form': form}
    return check_authorization_and_render(request, 'statistics/session_edit.html', context, s)


#################

@login_required(login_url='/login/')
def add(request, session_id):
    session = Session.objects.get(pk=session_id)
    committees = Committee.objects.filter(session=session).order_by('committee_name')
    session_subtopics = SubTopic.objects.filter(session=session)
    if request.method == 'POST':
        if request.POST.get('delete') == 'true':
            committee = Committee.objects.get(pk=request.POST.get('pk'))

            committee.delete()

            response_data = {}
            response_data['msg'] = 'Committee was deleted.'

            return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
            )
        else:
            pk = request.POST.get('pk')
            name = request.POST.get('name')
            topic = request.POST.get('topic')
            subtopics = json.loads(request.POST.get('subtopics'))

            response_data = {}
            form = CommitteeForm({'pk': pk, 'name': name, 'topic': topic})
            if form.is_valid():
                print 'Form is valid'
                committee_exists = False
                for committee in committees:
                    if committee.pk == form.cleaned_data['pk']:
                        committee_exists = True

                if committee_exists:
                    c = committees.filter(pk=form.cleaned_data['pk'])[0]
                else:
                    c = Committee()

                c.session = session
                c.committee_name = form.cleaned_data['name']
                c.committee_topic = form.cleaned_data['topic']
                c.save()

                subtopics_pretty_array = []
                committee_subtopics = SubTopic.objects.filter(committee=c)
                committee_new_subtopics = []
                for subtopic in subtopics:
                    if subtopic['pk'] != '':
                        subtopic_pk = int(subtopic['pk'])
                    else:
                        subtopic_pk = ''
                    for committee_subtopic in committee_subtopics:
                        print committee_subtopic.pk
                        print subtopic['pk']
                        if committee_subtopic.pk == subtopic_pk:
                            print 'subtopic exists'
                            subtopic_exists = True
                            break
                    else:
                        if subtopic['subtopic'] == 'General' and committee_subtopics.filter(subtopic_text='General'):
                            subtopic_exists = True
                            print 'subtopic exists'
                        else:
                            subtopic_exists = False
                            print 'subtopic was not there'

                    if subtopic_exists:
                        if subtopic['subtopic'] == 'General':
                            s = committee_subtopics.filter(subtopic_text='General')[0]
                        else:
                            s = committee_subtopics.get(pk=subtopic['pk'])
                    else:
                        s = SubTopic()

                    s.session = session
                    s.committee = c
                    s.subtopic_text = subtopic['subtopic']
                    s.save()
                    committee_new_subtopics.append(s)
                    subtopics_pretty_array.append(s.subtopic_text)

                print committee_subtopics
                print committee_new_subtopics
                for subtopic in committee_subtopics:
                    if subtopic not in committee_new_subtopics:
                        subtopic.delete()

                response_data['pk'] = c.pk
                response_data['subtopics'] = ', '.join(subtopics_pretty_array)

                return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                )

            else:
                print 'Form not valid'
                print form.errors
                response_data['errors'] = form.errors
                return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                )
    else:
        form = CommitteeForm()

    context = {'session': session, 'committees': committees, 'subtopics': session_subtopics, 'form': form}

    return check_authorization_and_render(request, 'statistics/session_add.html', context, session)


#################

@login_required(login_url='/login/')
def point(request, session_id, committee_id=None):
    # The Point view handles the submission of points, both creating the form from the data given, validating the form,
    # and sending the user to the right place if the data submission was successful.
    session = Session.objects.get(pk=session_id)
    # Get the committee and session of the committee that wants to make a point.

    if committee_id:
        render_committee = Committee.objects.get(pk=committee_id)
        all_form = False
    else:
        render_committee = ''
        all_form = True

    # Here we get the active debate, get the committee of the active debate and get the active round no.
    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)
    active_round_no = ActiveRound.objects.get(session__pk=session_id).active_round

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name), )
    # We need to make an array of each round with the round number and the place in the array
    # So we first make an array with the round numbers (1,2,3)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.session_max_rounds):
        n = i + 1
        max_rounds.append(n)
    # Then we make an array with the value and the position, so the form can accept the data.
    for r in max_rounds:
        max_rounds_array.append((r, r), )

    subtopics_array = []
    # Get the subtopics of the active committee, and the loop through each one to create an array of subtopics.
    if active_committee:
        if all_form:
            subtopics = SubTopic.objects.filter(session_id=session_id)
        else:
            subtopics = SubTopic.objects.filter(session_id=session_id).filter(committee=active_committee[0])
    else:
        subtopics = []
    for subtopic in subtopics:
        subtopics_array.append((subtopic.pk, subtopic.subtopic_text), )

    # If the user is trying to submit data (method=POST), take a look at it
    if request.method == 'POST':
        # Print what the user is trying to submit for the sake of server logs.
        print request.POST

        # Create an instance of the form and populate it with data from the request.
        form = PointForm(subtopics_array, request.POST)

        # Check if the form is valid.
        if form.is_valid():
            # Create a point from the data submitted
            point = Point(session=Session.objects.filter(session_name=form.cleaned_data['session'])[0],
                          committee_by=Committee.objects.filter(session__pk=session_id).filter(
                              committee_name=form.cleaned_data['committee'])[0],
                          active_debate=form.cleaned_data['debate'], active_round=form.cleaned_data['round_no'],
                          point_type=form.cleaned_data['point_type']
                          )
            # You need to first save the point before being able to add data to the ManyToManyField.
            point.save()
            # For each subtopic in the selected subtopics, add the subtopic to the saved points list of subtopics.
            for s in form.cleaned_data['subtopics']:
                st = SubTopic.objects.get(pk=s)
                point.subtopics.add(st)

            # Once all that is done, send the user to the thank you page.
            messages.add_message(request, messages.SUCCESS, 'Point Successfully Submitted')
            return HttpResponseRedirect(reverse('statistics:point', args=[session_id, committee_id]))

    else:
        # Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        if all_form:
            form = PointForm(subtopics_array, {'session': session.session_name, 'committee': '', 'debate': active,
                                               'round_no': active_round_no})
        else:
            form = PointForm(subtopics_array,
                             {'session': session.session_name, 'committee': render_committee.committee_name,
                              'debate': active, 'round_no': active_round_no})

    if all_form:
        context = {'debate': active, 'all_form': all_form, 'session': session, 'subtopics': subtopics, 'form': form,
                   'committees': committees_array, 'rounds': max_rounds_array}
    else:
        context = {'debate': active, 'all_form': all_form, 'committee': render_committee, 'session': session,
                   'subtopics': subtopics, 'form': form, 'committees': committees_array, 'rounds': max_rounds_array}
    return check_authorization_and_render(request, 'statistics/point_form.html', context, session, False)


#################


@login_required(login_url='/login/')
def content(request, session_id, committee_id=None):
    session = Session.objects.get(pk=session_id)

    if committee_id:
        render_committee = Committee.objects.get(pk=committee_id)
        all_form = False
    else:
        render_committee = ''
        all_form = True

    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name), )

    if request.method == 'POST':
        print request.POST

        form = ContentForm(request.POST)
        if form.is_valid():
            contentpoint = ContentPoint(session=Session.objects.filter(session_name=form.cleaned_data['session'])[0],
                                        committee_by=Committee.objects.filter(session__pk=session_id).filter(
                                            committee_name=form.cleaned_data['committee'])[0],
                                        active_debate=form.cleaned_data['debate'],
                                        point_type=form.cleaned_data['point_type'],
                                        point_content=form.cleaned_data['content']
                                        )
            contentpoint.save()
            messages.add_message(request, messages.SUCCESS, 'Content Point Successfully Submitted')
            return HttpResponseRedirect(reverse('statistics:content', args=[session_id, committee_id]))
    else:
        if all_form:
            form = ContentForm({'session': session.session_name, 'committee': '', 'debate': active})
        else:
            form = ContentForm(
                    {'session': session.session_name, 'committee': render_committee.committee_name, 'debate': active})

    if all_form:
        context = {'debate': active, 'session': session, 'form': form, 'committees': committees_array,
                   'all_form': all_form}
    else:
        context = {'debate': active, 'committee': render_committee, 'session': session, 'form': form,
                   'committees': committees_array, 'all_form': all_form}

    return check_authorization_and_render(request, 'statistics/content_form.html', context, session, False)


#################


@login_required(login_url='/login/')
def joint(request, session_id, committee_id=None):
    session = Session.objects.get(pk=session_id)

    if committee_id:
        render_committee = Committee.objects.get(pk=committee_id)
        all_form = False
    else:
        render_committee = ''
        all_form = True

    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)
    active_round_no = ActiveRound.objects.get(session__pk=session_id).active_round

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name), )
    # We need to make an array of each round with the round number and the place in the array
    # So we first make an array with the round numbers (1,2,3)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.session_max_rounds):
        n = i + 1
        max_rounds.append(n)
    # Then we make an array with the value and the position, so the form can accept the data.
    for r in max_rounds:
        max_rounds_array.append((r, r), )

    subtopics_array = []
    # Get the subtopics of the active committee, and the loop through each one to create an array of subtopics.
    if active_committee:
        subtopics = SubTopic.objects.filter(session_id=session_id).filter(committee=active_committee[0])
    else:
        subtopics = []
    for subtopic in subtopics:
        subtopics_array.append((subtopic.pk, subtopic.subtopic_text), )

    if request.method == 'POST':
        print request.POST

        form = JointForm(subtopics_array, request.POST)
        if form.is_valid():
            contentpoint = ContentPoint(session=Session.objects.filter(session_name=form.cleaned_data['session'])[0],
                                        committee_by=Committee.objects.filter(session__pk=session_id).filter(
                                            committee_name=form.cleaned_data['committee'])[0],
                                        active_debate=form.cleaned_data['debate'],
                                        point_type=form.cleaned_data['point_type'],
                                        point_content=form.cleaned_data['content']
                                        )
            contentpoint.save()
            # Create a point from the data submitted
            point = Point(session=Session.objects.filter(session_name=form.cleaned_data['session'])[0],
                          committee_by=Committee.objects.filter(session__pk=session_id).filter(
                              committee_name=form.cleaned_data['committee'])[0],
                          active_debate=form.cleaned_data['debate'], active_round=form.cleaned_data['round_no'],
                          point_type=form.cleaned_data['point_type']
                          )
            # You need to first save the point before being able to add data to the ManyToManyField.
            point.save()
            # For each subtopic in the selected subtopics, add the subtopic to the saved points list of subtopics.
            for s in form.cleaned_data['subtopics']:
                st = SubTopic.objects.filter(pk=s)
                point.subtopics.add(st[0])
            messages.add_message(request, messages.SUCCESS, 'Joint Point Successfully Submitted')
            return HttpResponseRedirect(reverse('statistics:joint', args=[session_id, committee_id]))
    else:
        if all_form:
            form = JointForm(subtopics_array, {'session': session.session_name, 'committee': '', 'debate': active,
                                               'round_no': active_round_no})
        else:
            form = JointForm(subtopics_array,
                             {'session': session.session_name, 'committee': render_committee.committee_name,
                              'debate': active, 'round_no': active_round_no})

    if all_form:
        context = {'debate': active, 'session': session, 'subtopics': subtopics, 'form': form, 'all_form': all_form,
                   'committees': committees_array, 'rounds': max_rounds_array, 'round_no': active_round_no}
    else:
        context = {'debate': active, 'committee': render_committee, 'session': session, 'subtopics': subtopics,
                   'form': form, 'all_form': all_form, 'committees': committees_array, 'rounds': max_rounds_array,
                   'round_no': active_round_no}

    return check_authorization_and_render(request, 'statistics/joint_form.html', context, session, False)


#################


@login_required(login_url='/login/')
def vote(request, session_id, committee_id=None):
    # The Vote form is just as complex as the Point form, and is made in a very similar manner.

    # We get the current session and debate of the user, then get the active committee from the active debate.
    session = Session.objects.get(pk=session_id)
    if committee_id:
        render_committee = Committee.objects.get(pk=committee_id)
        all_form = False
    else:
        render_committee = ''
        all_form = True
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name), )

    # If the user is trying to submit something:
    if request.method == 'POST':
        # Create an instance of the form and populate it with data from the request.
        form = VoteForm(request.POST)

        # If the data in the form is valid
        if form.is_valid():
            # Then make a vote from the data in the form.
            vote = Vote(session=Session.objects.filter(
                    session_name=form.cleaned_data['session'])[0],
                        committee_by=Committee.objects.filter(session__pk=session_id).filter(
                            committee_name=form.cleaned_data['committee'])[0],
                        active_debate=form.cleaned_data['debate'],
                        in_favour=form.cleaned_data['in_favour'],
                        against=form.cleaned_data['against'],
                        abstentions=form.cleaned_data['abstentions'],
                        absent=form.cleaned_data['absent']
                        )
            # Save the vote to the database.
            vote.save()
            # Then send the user a success message.
            messages.add_message(request, messages.SUCCESS, 'Point Successfully Submitted')
            return HttpResponseRedirect(reverse('statistics:vote', args=[session_id, committee_id]))

    else:
        # Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        if all_form:
            form = VoteForm(
                    {'session': session.session_name, 'committee': '', 'debate': active, 'in_favour': 0, 'against': 0,
                     'abstentions': 0, 'absent': 0})
        else:
            form = VoteForm(
                    {'session': session.session_name, 'committee': render_committee.committee_name, 'debate': active,
                     'in_favour': 0, 'against': 0, 'abstentions': 0, 'absent': 0})
    if all_form:
        context = {'session': session, 'debate': active, 'form': form, 'all_form': all_form,
                   'committees': committees_array}
    else:
        context = {'session': session, 'committee': render_committee, 'debate': active, 'form': form,
                   'all_form': all_form, 'committees': committees_array}

    return check_authorization_and_render(request, 'statistics/vote_form.html', context, session, False)


#################


@login_required(login_url='/login/')
def manage(request, session_id):
    # The manage page contains 2 forms, one form for changing the active debate and one form for changing the active round.

    # First we set up our variables, we need the session, the active debate, the active round, the max rounds and a list of committees
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0]
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_round = ActiveRound.objects.filter(session__pk=session_id)[0].active_round
    active_round_entry = ActiveRound.objects.filter(session__pk=session_id)[0]
    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name), )
    # We need to make an array of each round with the round number and the place in the array
    # So we first make an array with the round numbers (1,2,3)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.session_max_rounds):
        n = i + 1
        max_rounds.append(n)
    # Then we make an array with the value and the position, so the form can accept the data.
    for r in max_rounds:
        max_rounds_array.append((r, r), )

    # If the user is trying to submit data
    if request.method == 'POST':
        # For server log purposes, print response
        print request.POST
        # if it's an active debate submission
        if 'active_debate' in request.POST:
            # Create an instance of the form and populate it with data from the request.
            debate_form = ActiveDebateForm(committees_array, request.POST)
            # If it's valid
            if debate_form.is_valid():
                # Get the committee that you want to change the active debate to and then set the active debate to be the new committees committee name.
                active_debate_committee = Committee.objects.get(pk=debate_form.cleaned_data['active_debate'])
                active_debate.active_debate = active_debate_committee.committee_name
                # Save the new active debate
                active_debate.save()
                # Send the user to the manage page
                messages.add_message(request, messages.SUCCESS, 'Active Debate Saved')
                return HttpResponseRedirect(reverse('statistics:manage', args=[session_id]))
            else:
                print debate_form
            # You also have to create an empty/default instance of the "opposite" form, since we've got two on this page.
            round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})
        # otherwise if it's an active round submission
        elif 'active_round' in request.POST:
            # Create an instance of the form and populate it with data from the request.
            round_form = ActiveRoundForm(max_rounds_array, request.POST)
            # If the submission is valid
            if round_form.is_valid():
                # Change the active round entry to be the new round
                active_round_entry.active_round = round_form.cleaned_data['active_round']
                # Save the active round.
                active_round_entry.save()
                # Send the user back to the manage page
                messages.add_message(request, messages.SUCCESS, 'Active Round Saved')
                return HttpResponseRedirect(reverse('statistics:manage', args=[session_id]))
            debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})

    # Otherwise, give the User some nice new forms.
    else:
        debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})
        round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})
        point_form = PointEditForm([], {'session': session.session_name})
        content_form = ContentEditForm({'session': session.session_name})
        vote_form = VoteEditForm({'session': session.session_name})

    context = {'session': session, 'committees': committees, 'active': active, 'active_round': active_round,
               'debate_form': debate_form, 'round_form': round_form, 'point_form': point_form,
               'content_form': content_form, 'vote_form': vote_form}
    return check_authorization_and_render(request, 'statistics/manage.html', context, session)


#################


@login_required(login_url='/login/')
def predict(request, session_id, committee_id):
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.get(pk=committee_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active_debate)[0]
    active_subtopics = SubTopic.objects.filter(committee=active_committee)
    subtopics_next_array = []
    subtopics_array = []
    for subtopic in active_subtopics:
        subtopics_array.append((subtopic.pk, subtopic.subtopic_text), )
    # If the user is trying to submit data (method=POST), take a look at it
    if request.method == 'POST':
        # Print what the user is trying to submit for the sake of server logs.
        print request.POST

        # Create an instance of the form and populate it with data from the request.
        form = PredictForm(subtopics_array, request.POST)

        # Check if the form is valid.
        if form.is_valid():
            # For each subtopic in the selected subtopics, add the subtopic to the committees next_subtopics list.
            committee.next_subtopics.clear()
            for s in form.cleaned_data['next_subtopics']:
                st = SubTopic.objects.get(pk=s)
                committee.next_subtopics.add(st)

            # Once all that is done, send the user to the thank you page.
            messages.add_message(request, messages.SUCCESS, 'Point Successfully Predicted')
            return HttpResponseRedirect(reverse('statistics:predict', args=[session_id, committee_id]))

    else:
        # Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        form = PredictForm(subtopics_array, {'session': session, 'committee': committee})

    for subtopic in committee.next_subtopics.all():
        subtopics_next_array.append(subtopic.subtopic_text)
    edit_form = PredictEditForm()
    context = {'session': session, 'committee': committee, 'active_debate': active_debate, 'form': form,
               'edit_form': edit_form, 'next_subtopics': subtopics_next_array}

    return check_authorization_and_render(request, 'statistics/predict_form.html', context, session, False)


#################


@login_required(login_url='/login/')
def runningorder(request, session_id):
    # First we set up our variables, we need the session, the active debate, the active round, the max rounds and a list of committees
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0]
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_round = ActiveRound.objects.filter(session__pk=session_id)[0].active_round
    active_round_entry = ActiveRound.objects.filter(session__pk=session_id)[0]
    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name), )
    # We need to make an array of each round with the round number and the place in the array
    # So we first make an array with the round numbers (1,2,3)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.session_max_rounds):
        n = i + 1
        max_rounds.append(n)
    # Then we make an array with the value and the position, so the form can accept the data.
    for r in max_rounds:
        max_rounds_array.append((r, r), )

    # If the user is trying to submit data
    if request.method == 'POST':
        # For server log purposes, print response
        print request.POST
        # if it's an active debate submission
        if 'active_debate' in request.POST:
            # Create an instance of the form and populate it with data from the request.
            debate_form = ActiveDebateForm(committees_array, request.POST)
            # If it's valid
            if debate_form.is_valid():
                # Get the committee that you want to change the active debate to and then set the active debate to be the new committees committee name.
                active_debate_committee = Committee.objects.get(pk=debate_form.cleaned_data['active_debate'])
                active_debate.active_debate = active_debate_committee.committee_name
                # Save the new active debate
                active_debate.save()
                for committee in committees:
                    committee.next_subtopics.clear()
                # Send the user to the manage page
                messages.add_message(request, messages.SUCCESS, 'Active Debate Saved')
                return HttpResponseRedirect(reverse('statistics:runningorder', args=[session_id]))
            else:
                print debate_form
            # You also have to create an empty/default instance of the "opposite" form, since we've got two on this page.
            round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})
        # otherwise if it's an active round submission
        elif 'active_round' in request.POST:
            # Create an instance of the form and populate it with data from the request.
            round_form = ActiveRoundForm(max_rounds_array, request.POST)
            # If the submission is valid
            if round_form.is_valid():
                # Change the active round entry to be the new round
                active_round_entry.active_round = round_form.cleaned_data['active_round']
                # Save the active round.
                active_round_entry.save()
                # Send the user back to the manage page
                messages.add_message(request, messages.SUCCESS, 'Active Round Saved')
                return HttpResponseRedirect(reverse('statistics:runningorder', args=[session_id]))
            debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})

    # Otherwise, give the User some nice new forms.
    else:
        debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})
        round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})

    context = {'session': session, 'committees': committees, 'active': active, 'active_round': active_round,
               'debate_form': debate_form, 'round_form': round_form, 'no_footer': True}
    return check_authorization_and_render(request, 'statistics/runningorder.html', context, session)


def gender(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0]
    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name),)

    if request.method == 'POST':

        print(request.POST)

        gender_form = GenderForm(committees_array, request.POST)

        if gender_form.is_valid():
            committee = Committee.objects.get(pk=gender_form.cleaned_data['committee'])
            gender_point = Gender(committee=committee, gender=gender_form.cleaned_data['gender'])

            gender_point.save()

            # Then send the user a success message.
            messages.add_message(request, messages.SUCCESS, 'Gender Successfully Submitted')
            return HttpResponseRedirect(reverse('statistics:gender', args=[session_id]))
    else:
        gender_form = GenderForm(committees_array)

    content = {'session': session, 'committees': committees, 'active': active_debate, 'form': gender_form}

    return check_authorization_and_render(request, 'statistics/gender_form.html', content, session, False)
