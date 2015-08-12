import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

#Importing all models for statistics.
from .models import Session, Committee, Point, Vote, SubTopic, ActiveDebate, ActiveRound

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
    context = {'session_committee_list': session_committee_list, 'session_id': session_id, 'session': session}
    return render(request, 'statistics/session.html', context)

def debate(request, session_id, committee_id):
    #Same for debates as for sessions, the only static content is the name and data of the committee and the session.
    #The rest of the point/voting data comes through the api that can constantly be updated.
    c = Committee.objects.get(pk=committee_id)
    s = Session.objects.get(pk=session_id)
    context = {'committee': c, 'session': s}
    return render(request, 'statistics/debate.html', context)

def committee(request, session_id, committee_id):
    #The idea is not only to have a "debate page", where you can see how many points are made during the debate of a particular resolution,
    #but also for there to be a "committee page", where delegates can see how many points their committee has made during each debate, what was the longest time between points etc.
    #This should be made in due time.
    pass

def point(request, session_id, committee_id):
    #The Point view handles the submission of points, both creating the form from the data given, validating the form,
    #and sending the user to the right place if the data submission was successful.
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)
    active_round = ActiveRound.objects.filter(session__pk=session_id)
    active_round_no = active_round[0].active_round

    subtopics = SubTopic.objects.filter(committee=active_committee[0])
    subtopics_array = []
    for subtopic in subtopics:
        subtopics_array.append((subtopic.pk, subtopic.subtopic_text),)
    committee = Committee.objects.get(pk=committee_id)
    session = Session.objects.get(pk=session_id)

    if request.method == 'POST':
        print request.POST
        form = PointForm(subtopics_array, request.POST)
        if form.is_valid():
            subtopic_submit_array = []

            point = Point(session = Session.objects.filter(session_name=form.cleaned_data['session'])[0], committee_by=Committee.objects.filter(session__pk=session_id).filter(committee_name=form.cleaned_data['committee'])[0], active_debate=form.cleaned_data['debate'], active_round=form.cleaned_data['round_no'], point_type=form.cleaned_data['point_type'])
            point.save()
            for s in form.cleaned_data['subtopics']:
                st = SubTopic.objects.filter(pk=s)
                point.subtopics.add(st[0])

            return HttpResponseRedirect('/session/' + session_id + '/point/' + committee_id + '/thanks')

    else:
        form = PointForm(subtopics_array, {'session': session.session_name, 'committee': committee.committee_name, 'debate': active, 'round_no': active_round_no})


    context = {'debate': active, 'committee': committee, 'session': session, 'subtopics': subtopics, 'form': form}
    return render(request, 'statistics/point.html', context)

def vote(request, session_id, committee_id):
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.get(pk=committee_id)
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(committee_name=active)

    if request.method == 'POST':
        form = VoteForm(request.POST)

        if form.is_valid():
            vote = Vote(session = Session.objects.filter(session_name=form.cleaned_data['session'])[0], committee_by=Committee.objects.filter(session__pk=session_id).filter(committee_name=form.cleaned_data['committee'])[0], active_debate=form.cleaned_data['debate'], in_favour=form.cleaned_data['in_favour'], against=form.cleaned_data['against'], abstentions=form.cleaned_data['abstentions'], absent=form.cleaned_data['absent'])
            vote.save()
            return HttpResponseRedirect('/session/' + session_id + '/vote/' + committee_id + '/thanks')

    else:
        form = VoteForm({'session': session.session_name, 'committee': committee.committee_name, 'debate': active, 'in_favour': 0, 'against': 0, 'abstentions': 0, 'absent': 0})

    context = {'session': session, 'committee': committee, 'debate': active, 'form': form}
    return render(request, 'statistics/vote.html', context)

def thanks(request, session_id, committee_id):
    thanks_url = '/session/' + session_id + '/point/' + committee_id
    context = {'thanks_url': thanks_url}
    return render(request, 'statistics/thanks.html', context)

def vote_thanks(request, session_id, committee_id):
    thanks_url = '/session/' + session_id + '/vote/' + committee_id
    context = {'thanks_url': thanks_url}
    return render(request, 'statistics/thanks.html', context)

def manage(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0]
    active = ActiveDebate.objects.filter(session_id=session_id)[0].active_debate
    active_round = ActiveRound.objects.filter(session__pk=session_id)[0].active_round
    active_round_entry = ActiveRound.objects.filter(session__pk=session_id)[0]
    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    for committee in committees:
        committees_array.append((committee.pk, committee.committee_name),)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.session_max_rounds):
        n = i + 1
        max_rounds.append(n)
    for r in max_rounds:
        max_rounds_array.append((r, r),)

    if request.method == 'POST':
        print request.POST
        if 'active_debate' in request.POST:
            debate_form = ActiveDebateForm(committees_array, request.POST)
            if debate_form.is_valid():
                active_debate_committee = Committee.objects.get(pk=debate_form.cleaned_data['active_debate'])
                active_debate.active_debate = active_debate_committee.committee_name
                active_debate.save()
                return HttpResponseRedirect('/session/' + session_id + '/manage')
            else:
                print debate_form
            round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})
        elif 'active_round' in request.POST:
            round_form = ActiveRoundForm(max_rounds_array, request.POST)
            if round_form.is_valid():
                active_round_entry.active_round = round_form.cleaned_data['active_round']
                active_round_entry.save()
                return HttpResponseRedirect('/session/' + session_id + '/manage')
            debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})

    else:
        debate_form = ActiveDebateForm(committees_array, {'session': session.session_name})
        round_form = ActiveRoundForm(max_rounds_array, {'session': session.session_name})

    context = {'session': session, 'committees': committees, 'active': active, 'active_round': active_round, 'debate_form': debate_form, 'round_form': round_form}
    return render(request, 'statistics/manage.html', context)

def session_api(request, session_id):
    committees = Committee.objects.filter(session__id=session_id)
    points = Point.objects.filter(session_id=session_id).filter(point_type='P')
    drs = Point.objects.filter(session_id=session_id).filter(point_type='DR')
    votes = Vote.objects.filter(session_id=session_id)
    committee_list = []
    points_list = []
    drs_list = []

    in_favour = []
    against = []
    abstentions = []
    absent = []

    for committee in committees:
        c = committee.committee_name
        p = points.filter(committee_by=committee).count()
        d = drs.filter(committee_by=committee).count()
        committee_list.append(c)
        points_list.append(p)
        drs_list.append(d)

        debate_in_favour = 0
        debate_against = 0
        debate_abstentions = 0
        debate_absent = 0

        v = votes.filter(active_debate=committee)
        for vc in v:
            debate_in_favour += vc.in_favour
            debate_against += vc.against
            debate_abstentions += vc.abstentions
            debate_absent += vc.absent

        in_favour.append(debate_in_favour)
        against.append(debate_against)
        abstentions.append(debate_abstentions)
        absent.append(debate_absent)

    session_json = json.dumps({
    'committees': committee_list,
    'points': points_list,
    'drs': drs_list,
    'in_favour': in_favour,
    'against': against,
    'abstentions': abstentions,
    'absent': absent
    })
    return HttpResponse(session_json, content_type='json')

def debate_api(request, session_id, committee_id):
    active_debate = ActiveDebate.objects.filter(session__pk=session_id)
    active_round = ActiveRound.objects.filter(session__pk=session_id)
    active_round_no = active_round[0].active_round

    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.filter(pk=committee_id)
    committees = Committee.objects.filter(session__id=session_id)
    committee_array_name = []
    committee_array_name.append(committee[0].committee_name)

    all_points = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name)
    points = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name).filter(point_type='P')
    drs = Point.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name).filter(point_type='DR')
    votes = Vote.objects.filter(session__pk=session_id).filter(active_debate=committee[0].committee_name)

    if not all_points:
        pass
    else:
        latest_point_name = all_points.order_by('-timestamp')[0].committee_by.committee_name
        latest_point_subtopics = all_points.order_by('-timestamp')[0].subtopics.all()
        latest_point_subtopics_array = []

        for s in latest_point_subtopics:
            latest_point_subtopics_array.append(s.subtopic_text)

        subtopics = SubTopic.objects.filter(session__pk=session_id).filter(committee__committee_name=committee[0].committee_name)
        no_rounds = range(session.session_max_rounds)
        subtopics_array = []
        subtopic_points_array = []

        for s in subtopics:
            subtopics_array.append(s.subtopic_text)

        for r in no_rounds:
            r_n = r + 1
            round_array = []
            round_points = all_points.filter(active_round=r_n)
            for s in subtopics:
                round_array.append(round_points.filter(subtopics=s).count())

            subtopic_points_array.append(round_array)

        is_active = active_debate[0].active_debate == committee[0].committee_name

    committees_list = []
    committees_voted_list = []

    points_total = 0
    type_point = 0
    type_dr = 0

    points_made = []
    drs_made = []

    debate_in_favour = 0
    debate_against = 0
    debate_abstentions = 0
    debate_absent = 0
    total_counted = 0

    committees_in_favour = []
    committees_against = []
    committees_abstentions = []
    committees_absent = []

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

    for v in votes:
        debate_in_favour += v.in_favour
        debate_against += v.against
        debate_abstentions += v.abstentions
        debate_absent += v.absent
        total = v.in_favour + v.against + v.abstentions + v.absent
        total_counted += total

        committees_in_favour.append(v.in_favour)
        committees_against.append(v.against)
        committees_abstentions.append(v.abstentions)
        committees_absent.append(v.absent)

        committees_voted_list.append(v.committee_by.committee_name)


    committees_count = len(committees_list)
    committees_voted = len(committees_voted_list)

    debate_in_favour_array = []
    debate_against_array = []
    debate_abstentions_array = []
    debate_absent_array = []

    debate_in_favour_array.append(debate_in_favour)
    debate_against_array.append(debate_against)
    debate_abstentions_array.append(debate_abstentions)
    debate_absent_array.append(debate_absent)

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
