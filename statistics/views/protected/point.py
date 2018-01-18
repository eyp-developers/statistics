from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statistics.models import Session, Committee, SubTopic, ActiveDebate, \
                                ActiveRound, Point
from statistics.forms.point import PointForm
from helpers import check_authorization_and_render


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

    # If the user is trying to submit data (method=POST), take a look at it
    if request.method == 'POST':

        # Create an instance of the form and populate it with data from the request.
        form = PointForm(subtopics_array, request.POST)

        # Check if the form is valid.
        if form.is_valid():
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
                st = SubTopic.objects.get(pk=s)
                point.subtopics.add(st)

            # Once all that is done, send the user to the thank you page.
            messages.add_message(request, messages.SUCCESS, 'Point Successfully Submitted')
            if all_form:
                return HttpResponseRedirect(reverse('statistics:point_all', args=[session_id]))
            else:
                return HttpResponseRedirect(reverse('statistics:point', args=[session_id, committee_id]))

    else:
        # Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        if all_form:
            form = PointForm(subtopics_array, {'session': session.name, 'committee': '', 'debate': active,
                                               'round_no': active_round_no})
        else:
            form = PointForm(subtopics_array,
                             {'session': session.name, 'committee': render_committee.name,
                              'debate': active, 'round_no': active_round_no})

    if all_form:
        context = {'debate': active, 'all_form': all_form, 'session': session, 'subtopics': subtopics, 'form': form,
                   'committees': committees_array, 'rounds': max_rounds_array}
    else:
        context = {'debate': active, 'all_form': all_form, 'committee': render_committee, 'session': session,
                   'subtopics': subtopics, 'form': form, 'committees': committees_array, 'rounds': max_rounds_array}
    return check_authorization_and_render(request, 'statistics/point_form.html', context, session, False)
