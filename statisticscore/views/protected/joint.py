from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statisticscore.models import Session, Committee, SubTopic, ActiveDebate, \
                                ActiveRound, ContentPoint, Point
from statisticscore.forms.joint import JointForm
from helpers import check_authorization_and_render


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
    active_committee = Committee.objects.filter(session__pk=session_id).filter(name=active)
    active_round_no = ActiveRound.objects.get(session__pk=session_id).active_round

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.name), )
    # We need to make an array of each round with the round number and the place in the array
    # So we first make an array with the round numbers (1,2,3)
    max_rounds = []
    max_rounds_array = []
    for i in range(session.max_rounds):
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
        if all_form:
            subtopic_committee = subtopic.committee.name
            subtopics_array.append((subtopic.pk, subtopic.text + " - " + subtopic_committee))
        else:
            subtopics_array.append((subtopic.pk, subtopic.text), )

    if request.method == 'POST':

        form = JointForm(subtopics_array, request.POST)
        if form.is_valid():
            contentpoint = ContentPoint(session=Session.objects.filter(name=form.cleaned_data['session'])[0],
                                        committee_by=Committee.objects.filter(session__pk=session_id).filter(
                                            name=form.cleaned_data['committee'])[0],
                                        active_debate=form.cleaned_data['debate'],
                                        point_type=form.cleaned_data['point_type'],
                                        point_content=form.cleaned_data['content']
                                        )
            contentpoint.save()
            # Create a point from the data submitted
            point = Point(session=Session.objects.filter(name=form.cleaned_data['session'])[0],
                          committee_by=Committee.objects.filter(session__pk=session_id).filter(
                              name=form.cleaned_data['committee'])[0],
                          active_debate=form.cleaned_data['debate'], active_round=form.cleaned_data['round_no'],
                          point_type=form.cleaned_data['point_type']
                          )

            # You need to first save the point before being able to add data to the ManyToManyField.
            point.save()
            # For each subtopic in the selected subtopics, add the subtopic to the saved points list of subtopics.
            for s in form.cleaned_data['subtopics']:
                st = SubTopic.objects.filter(pk=s)
                point.subtopics.add(st[0])
            messages.add_message(request, messages.SUCCESS, 'Point Successfully Submitted')
            if all_form:
                return HttpResponseRedirect(reverse('statisticscore:joint_all', args=[session_id]))
            else:
                return HttpResponseRedirect(reverse('statisticscore:joint', args=[session_id, committee_id]))
    else:
        if all_form:
            form = JointForm(subtopics_array, {'session': session.name, 'committee': '', 'debate': active,
                                               'round_no': active_round_no})
        else:
            form = JointForm(subtopics_array,
                             {'session': session.name, 'committee': render_committee.name,
                              'debate': active, 'round_no': active_round_no})

    if all_form:
        context = {'debate': active, 'session': session, 'subtopics': subtopics, 'form': form, 'all_form': all_form,
                   'committees': committees_array, 'rounds': max_rounds_array, 'round_no': active_round_no}
    else:
        context = {'debate': active, 'committee': render_committee, 'session': session, 'subtopics': subtopics,
                   'form': form, 'all_form': all_form, 'committees': committees_array, 'rounds': max_rounds_array,
                   'round_no': active_round_no}

    return check_authorization_and_render(request, 'statisticscore/joint_form.html', context, session, False)
