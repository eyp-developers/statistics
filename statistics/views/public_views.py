import time
import json

from datetime import date
from datetime import datetime
from time import strftime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages

# Importing all models for statistics.
from ..models import Session, Committee, Point, ContentPoint, Vote, SubTopic, ActiveDebate, ActiveRound

# Importing the forms too.
from ..forms import SessionForm, SessionEditForm, PointForm, VoteForm, ContentForm, JointForm, ActiveDebateForm, \
    ActiveRoundForm


def home(request):
    # All the home page needs is a list of the first few sessions ordered by the start date, then more pages with the rest of the sessions. We create the list, then the context and finally render the template.
    latest_sessions_list = Session.objects.filter(session_is_visible=True).order_by('-session_start_date')

    # class Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)
    paginator = Paginator(latest_sessions_list, 2)

    page = request.GET.get("page")
    try:
        latest_sessions_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        latest_sessions_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        latest_sessions_list = paginator.page(paginator.num_pages)



    active_sessions = []
    for session in Session.objects.all():
        if Point.objects.filter(session=session):
            latest_point = Point.objects.filter(session=session).order_by('-timestamp')[0].timestamp.date()
        else:
            latest_point = time.strptime("23/05/1996", "%d/%m/%Y")
        if ContentPoint.objects.filter(session=session):
            latest_content = ContentPoint.objects.filter(session=session).order_by('-timestamp')[0].timestamp.date()
        else:
            latest_content = time.strptime("23/05/1996", "%d/%m/%Y")
        if Vote.objects.filter(session=session):
            latest_vote = Vote.objects.filter(session=session).order_by('-timestamp')[0].timestamp.date()
        else:
            latest_vote = time.strptime("23/05/1996", "%d/%m/%Y")
        today = datetime.now().date()
        if (latest_point == today) or (latest_content == today) or (latest_vote == today):
            active_sessions.append(session)

    context = {'latest_sessions_list': latest_sessions_list, 'active_sessions': active_sessions}
    user = request.user
    if user.get_username() and not user.is_superuser:
        for session in Session.objects.all():
            if user == session.session_admin_user:
                admin_session = session
                context = {'latest_sessions_list': latest_sessions_list, 'active_sessions': active_sessions,
                           'admin_session': True, 'session': session}

    return render(request, 'statistics/home.html', context)


def get_started(request):
    return render(request, 'statistics/get_started.html')


def session(request, session_id):
    # The Session page uses static content and content that is constantly updated, the satic content is loaded with the view
    # and the updating content updates with the session api, defined further down.

    # The static data here is simply a list of the available committees (we can assume those don't change during live statistics)
    # and the name and data of the session itself.
    session_committee_list = Committee.objects.filter(session__id=session_id).order_by('committee_name')
    session = Session.objects.get(pk=session_id)

    no_stats = True
    # Getting the latest of everything to check if the date of them was today.
    if Point.objects.filter(session=session):
        latest_point = Point.objects.filter(session=session).order_by('-timestamp')[0].timestamp.date()
        no_stats = False
    else:
        latest_point = time.strptime("23/05/1996", "%d/%m/%Y")
    if ContentPoint.objects.filter(session=session):
        latest_content = ContentPoint.objects.filter(session=session).order_by('-timestamp')[0].timestamp.date()
        no_stats = False
    else:
        latest_content = time.strptime("23/05/1996", "%d/%m/%Y")
    if Vote.objects.filter(session=session):
        latest_vote = Vote.objects.filter(session=session).order_by('-timestamp')[0].timestamp.date()
        no_stats = False
    else:
        latest_vote = time.strptime("23/05/1996", "%d/%m/%Y")
    today = datetime.now().date()
    if (latest_point == today) or (latest_content == today) or (latest_vote == today):
        active_debate = ActiveDebate.objects.filter(session=session)[0].active_debate
        active_debate_committee = Committee.objects.filter(session=session).filter(committee_name=active_debate)[0]
    else:
        active_debate = []
        active_debate_committee = []
    voting_enabled = session.session_voting_enabled
    context = {'session_committee_list': session_committee_list, 'session_id': session_id, 'session': session,
               'voting_enabled': voting_enabled, 'active_debate': active_debate,
               'active_debate_committee': active_debate_committee, 'no_stats': no_stats}
    return render(request, 'statistics/session.html', context)


def debate(request, session_id, committee_id):
    # Same for debates as for sessions, the only static content is the name and data of the committee and the session.
    # The rest of the point/voting data comes through the api that can constantly be updated.
    c = Committee.objects.get(pk=committee_id)
    s = Session.objects.get(pk=session_id)
    # The statistics_type will let us render different templates based on the statistics selected by the user.
    statistics_type = s.session_statistics
    print statistics_type

    no_stats = True
    # Getting the latest of everything to check if the date of them was today.
    if Point.objects.filter(session=s):
        no_stats = False
    elif ContentPoint.objects.filter(session=s):
        no_stats = False
    elif Vote.objects.filter(session=s):
        no_stats = False

    # The voting enabled option lets us change the html content and js so that the voting is not displayed.
    voting_enabled = s.session_voting_enabled
    context = {'committee': c, 'session': s, 'statistics_type': statistics_type, 'voting_enabled': voting_enabled,
               'no_stats': no_stats}

    if statistics_type == 'JF':  # Should use or statement
        return render(request, 'statistics/joint.html', context)
    elif statistics_type == 'SF':
        return render(request, 'statistics/joint.html', context)
    elif statistics_type == 'S':
        return render(request, 'statistics/statistics.html', context)
    elif statistics_type == 'C':
        return render(request, 'statistics/content.html', context)
    elif statistics_type == 'R':
        return render(request, 'statistics/statistics.html', context)
    elif statistics_type == 'RC':
        return render(request, 'statistics/joint.html', context)
    else:
        pass


def committee(request, session_id, committee_id):
    # The idea is not only to have a "debate page", where you can see how many points are made during the debate of a particular resolution,
    # but also for there to be a "committee page", where delegates can see how many points their
    # committee has made during each debate, what was the longest time between points etc.
    # This should be made in due time.
    pass


def create_session(request):
    # If the user is trying to create a session
    if request.method == 'POST':
        # Fill an instance of a SessionForm with the request data.
        form = SessionForm(request.POST)

        if form.is_valid():
            # We need to set up time variables for the start and end of sessions.
            # We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            # We need to turn the voting 'True' and 'False' strings into actual booleans.
            if form.cleaned_data['voting'] == 'True':
                voting = True
            else:
                voting = False

            # Creating a lowercase string with no spaces from the session name to use for usernames
            name = ''.join(form.cleaned_data['name'].split()).lower()

            # Creating the Admin user
            admin_user = User.objects.create_user(username=name + '_admin',
                                                  email=form.cleaned_data['email'],
                                                  password=form.cleaned_data['admin_password'])

            # Adding the admin user to the admin group.
            admin_group = Group.objects.get(name='SessionAdmin')
            admin_group.user_set.add(admin_user)

            authenticate(username=admin_user.username, password=admin_user.password)

            # Creating the Submit user
            submit_user = User.objects.create_user(username=name,
                                                   email=form.cleaned_data['email'],
                                                   password=form.cleaned_data['submit_password'])

            # Adding the Submit user to the submit group.
            submit_group = Group.objects.get(name='SessionSubmit')
            submit_group.user_set.add(submit_user)

            # We need to create a session, active debate and active round.
            # We also need to create 2 new users for the session.
            session = Session(session_name=form.cleaned_data['name'],
                              session_description=form.cleaned_data['description'],
                              session_email=form.cleaned_data['email'],
                              session_picture=form.cleaned_data['picture'],
                              session_website_link=form.cleaned_data['website'],
                              session_facebook_link=form.cleaned_data['facebook'],
                              session_twitter_link=form.cleaned_data['twitter'],
                              session_country=form.cleaned_data['country'],
                              session_start_date=start_date,
                              session_end_date=end_date,
                              session_statistics=form.cleaned_data['statistics'],
                              session_color="indigo",
                              session_is_visible=False,
                              session_voting_enabled=voting,
                              session_max_rounds=form.cleaned_data['max_rounds'],
                              session_admin_user=admin_user,
                              session_submission_user=submit_user,
                              )
            session.save()
            active_debate = ActiveDebate(session=session, active_debate='')
            active_debate.save()
            active_round = ActiveRound(session=session, active_round=1)
            active_round.save()

            # Once we've done all that, lets say thanks for all that hard work.
            return HttpResponseRedirect(reverse('statistics:welcome', args=[session.pk]))
        else:
            print 'Wasnt valid'
            print form.errors
    else:
        # Otherwise, create a nice new form for the user.
        form = SessionForm()

    context = {'form': form}
    return render(request, 'statistics/session_create.html', context)
