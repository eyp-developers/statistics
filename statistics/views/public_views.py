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
