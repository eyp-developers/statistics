import time
import json
from collections import deque

from datetime import date
from datetime import datetime
from django.utils import timezone
from time import strftime

from decimal import Decimal

import operator

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.text import slugify

# Import the markdown parser used to display the changelog nicely
import mistune

# Import urllib2 to make a request to GitHub to get the latest changelog
import urllib2

# Importing all models for statistics.
from ..models import Session, Committee, Point, ContentPoint, Vote, SubTopic, ActiveDebate, ActiveRound, Announcement

# Importing the forms too.
from ..forms import SessionForm, SessionEditForm, PointForm, VoteForm, ContentForm, JointForm, ActiveDebateForm, \
    ActiveRoundForm


def home(request):
    # The home page needs a list of the first few sessions ordered by the start date, then more pages with the rest of the sessions.
    latest_sessions_list = Session.objects.filter(session_is_visible=True).order_by('-session_start_date')

    # class Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)
    paginator = Paginator(latest_sessions_list, 12)

    # The next line gets arguments from URLs like this https://stats.eyp.org/?page=2
    page = request.GET.get("page")
    try:
        latest_sessions_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        latest_sessions_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        latest_sessions_list = paginator.page(paginator.num_pages)

    # In this array we will store all the sessions which had activity today
    active_sessions = []
    today = timezone.now().date()
    # We could check all sessions, but if a session is so old it's not on the front-page anymore, we won't show it's activity.
    # Therefore, using latest_sessions_list saves a lot of database queries
    # latest_sessions_list only contains the sessions which show on the current page, due to how it's modified through the paginator.
    # This also means, that if a user visits later pages, they won't see the current activity anymore, which makes sense, since they are probably not interested if they're looking for an older session
    # Since this check is still quite expensive on the database (minimum 36 queries per 12 sessions per page) we will skip this completely, if the user is not on the first page.
    if (not page) or (int(page) == 1):
        for session in latest_sessions_list:
            iteration_latest_activity = session.session_latest_activity()
            if (iteration_latest_activity != False) and (iteration_latest_activity.date() == today):
                active_sessions.append(session)

    # We want to show all announcements on the hompage which have not expired yet
    announcements = Announcement.objects.filter(announcement_valid_until__gte=timezone.now())

    context = {
        'latest_sessions_list': latest_sessions_list,
        'active_sessions': active_sessions,
        'announcements': announcements
    }

    user = request.user
    if user.get_username() and not user.is_superuser:
        for session in Session.objects.all():
            if user == session.session_admin_user:
                # This appends the two key pairs to the context dictionary
                context.update({
                    'admin_session': True,
                    'session': session,
                })

    return render(request, 'statistics/home.html', context)


def get_started(request):
    return render(request, 'statistics/get_started.html')

def changelog(request):

    # Get the raw markdown from GitHub
    url = "https://raw.githubusercontent.com/eyp-developers/statistics/master/CHANGELOG.md"

    raw_markdown = urllib2.urlopen(url).read()

    # Render the markdown
    rendered_markdown = mistune.markdown(raw_markdown)

    # Pass the rendered markdown on to the template, where it will be inserted
    context = {'changelog': rendered_markdown}

    return render(request, 'statistics/changelog.html', context)


def session(request, session_id):
    # The Session page uses static content and content that is constantly updated, the static content is loaded with the view
    # and the updating content updates with the session api, defined in its own file.

    # The static data here is simply a list of the available committees (we can assume those don't change during live statistics)
    # and the name and data of the session itself.
    session = Session.objects.get(pk=session_id)
    session_committee_list = Committee.objects.filter(session=session).order_by('committee_name')

    # We initialise the values of active_debate and active_debate_committee with False, so that we don't get an error when we reference them in the contect dictionary
    context = {
        'session_committee_list': session_committee_list,
        'session': session,
        'active_debate': False,
        'active_debate_committee': False,
    }
    # This is the date and time of the latest activity of this session or False, if there was never any activity
    latest_activity = session.session_latest_activity()

    # In a moment, we will use today's date to check if there was any activity in the session today
    today = datetime.now().date()

    # It's important we only call date() on the result of session_latest_activity() if we know it's not False
    # This is why this part of the code is also inside the if latest_activity block
    # If it was false, we would get an error, because we can't call date() on a boolean
    if latest_activity and latest_activity.date() == today:
        active_debate = ActiveDebate.objects.get(session=session).active_debate
        
        context.update({
            'active_debate': active_debate,
            'active_debate_committee': Committee.objects.filter(session=session).get(committee_name=active_debate),
        })

    return render(request, 'statistics/session.html', context)


def debate(request, session_id, committee_id):
    # Same for debates as for sessions, the only static content is the name and data of the committee and the session.
    # The rest of the point/voting data comes through the api that can constantly be updated.
    c = Committee.objects.get(pk=committee_id)
    s = Session.objects.get(pk=session_id)
    # The statistics_type will let us render different templates based on the statistics selected by the user.
    statistics_type = s.session_statistics

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
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            # We need to set up time variables for the start and end of sessions.
            # We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            # We need to turn the voting 'True' and 'False' strings into actual booleans.
            if form.cleaned_data['voting_enabled'] == 'True':
                voting = True
            else:
                voting = False

            if form.cleaned_data['gender_statistics'] == 'True':
                gender = True
            else:
                gender = False

            # Creating a lowercase string with no spaces from the session name to use for usernames
            name = slugify(''.join(form.cleaned_data['name'].split()).lower())

            # Creating the Admin user
            admin_user = User.objects.create_user(username=name + '_admin',
                                                  email=form.cleaned_data['email'],
                                                  password=form.cleaned_data['admin_password'])


            user = authenticate(username=admin_user.username, password=form.cleaned_data['admin_password'])

            if user is not None:
                login(request, user)

            # Creating the Submit user
            submit_user = User.objects.create_user(username=name,
                                                   email=form.cleaned_data['email'],
                                                   password=form.cleaned_data['submission_password'])


            # We need to create a session, active debate and active round.
            # We also need to create 2 new users for the session.
            session = Session(session_name=form.cleaned_data['name'],
                              session_description=form.cleaned_data['description'],
                              session_type=form.cleaned_data['type'],
                              session_email=form.cleaned_data['email'],
                              session_picture_author=form.cleaned_data['picture_author'],
                              session_picture_author_link=form.cleaned_data['picture_author_link'],
                              session_picture_license=form.cleaned_data['picture_license'],
                              session_picture_license_link=form.cleaned_data['picture_license_link'],
                              session_website_link=form.cleaned_data['website'],
                              session_facebook_link=form.cleaned_data['facebook'],
                              session_twitter_link=form.cleaned_data['twitter'],
                              session_resolution_link=form.cleaned_data['resolution'],
                              session_country=form.cleaned_data['country'],
                              session_start_date=start_date,
                              session_end_date=end_date,
                              session_statistics=form.cleaned_data['statistics'],
                              session_color="indigo",
                              session_is_visible=False, # When created, all sessions are initially hidden from the front page.
                              session_voting_enabled=voting,
                              session_gender_enabled=gender,
                              gender_number_female=form.cleaned_data['number_female_participants'],
                              gender_number_male=form.cleaned_data['number_male_participants'],
                              gender_number_other=form.cleaned_data['number_other_participants'],
                              session_max_rounds=form.cleaned_data['max_rounds'],
                              session_admin_user=admin_user,
                              session_submission_user=submit_user,
                              )
            session.session_picture = form.cleaned_data['picture']
            session.save()
            active_debate = ActiveDebate(session=session, active_debate='')
            active_debate.save()
            active_round = ActiveRound(session=session, active_round=1)
            active_round.save()

            # Once we've done all that, lets say thanks for all that hard work and redirect the user to the new session.
            return HttpResponseRedirect(reverse('statistics:overview', args=[session.pk]))
    else:
        # Otherwise, create a nice new form for the user.
        form = SessionForm()

    announcements = Announcement.objects.filter(announcement_valid_until__gte=datetime.now())


    context = {'form': form, 'announcements': announcements}
    return render(request, 'statistics/session_create.html', context)

def high_scores(request):

    most_votes = dict()
    most_in_favour = dict()
    most_against = dict()
    most_points = dict()
    most_drs = dict()
    most_points_in_debate = dict()
    most_drs_in_debate = dict()
    most_successful = dict()
    most_unsuccessful = dict()
    best_mpp = dict()
    stats = False

    for s in Session.objects.all():
        if Point.objects.all().filter(session=s).count() != 0:
            stats = True

        if s.session_is_visible and ((not s.session_has_technical_problems) and stats):
            total_votes = 0
            in_favour = 0
            against = 0
            abstentions = 0
            votes = Vote.objects.filter(session__id=s.pk)
            for vote in votes:
                in_favour += vote.in_favour
                against += vote.against
                abstentions += vote.abstentions
                total_votes += vote.total_votes()
                if in_favour != 0 and total_votes != 0 and against != 0:
                    percent_in_favour = (Decimal(in_favour) / Decimal(total_votes)) * 100
                    percent_against = (Decimal(against) / Decimal(total_votes)) * 100
                    most_in_favour[s.session_name] = percent_in_favour
                    most_against[s.session_name] = percent_against

            most_votes[s.session_name] = total_votes

            total_points = 0
            total_drs = 0
            total_successful = 0
            total_unsuccessful = 0
            committees = Committee.objects.filter(session=s)
            for c in committees:
                if c.voting_successful():
                    total_successful += 1
                else:
                    total_unsuccessful += 1

                points = c.num_points()
                drs = c.num_drs()

                total_points += points
                total_drs += drs
                most_points_in_debate[c.committee_name + ', ' + s.session_name] = points
                most_drs_in_debate[c.committee_name + ', ' + s.session_name] = drs

            most_points[s.session_name] = total_points
            most_drs[s.session_name] = total_drs
            most_successful[s.session_name] = total_successful
            most_unsuccessful[s.session_name] = total_unsuccessful
            if s.minutes_per_point() != 0:
                best_mpp[s.session_name] = s.minutes_per_point()

    five_most_votes = sorted(most_votes.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_in_favour = sorted(most_in_favour.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_against = sorted(most_against.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_points = sorted(most_points.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_drs = sorted(most_drs.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_points_in_debate = sorted(most_points_in_debate.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_drs_in_debate = sorted(most_drs_in_debate.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_successful = sorted(most_successful.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_unsuccessful = sorted(most_unsuccessful.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_best_mpp = sorted(best_mpp.items(), key=operator.itemgetter(1))[:5]

    context = {'top_voters': five_most_votes,
               'top_in_favour': five_most_in_favour,
               'top_against': five_most_against,
               'top_points': five_most_points,
               'top_drs': five_most_drs,
               'top_points_in_debate': five_most_points_in_debate,
               'top_drs_in_debate': five_most_drs_in_debate,
               'top_successful': five_most_successful,
               'top_unsuccessful': five_most_unsuccessful,
               'top_mpp': five_best_mpp,
               }
    return render(request, 'statistics/high_scores.html', context)


def handler404(request):
    return render(request, 'statistics/404.html')


def handler500(request):
    return render(request, 'statistics/404.html')
