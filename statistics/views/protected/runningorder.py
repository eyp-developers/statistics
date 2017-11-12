from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statistics.models import Session, Committee, SubTopic, ActiveDebate, \
                              ActiveRound
from statistics.forms.active import ActiveDebateForm, ActiveRoundForm
from helpers import check_authorization_and_render


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

    # If the user is trying to submit data
    if request.method == 'POST':
        # if it's an active debate submission
        if 'active_debate' in request.POST:
            # Create an instance of the form and populate it with data from the request.
            debate_form = ActiveDebateForm(committees_array, request.POST)
            # If it's valid
            if debate_form.is_valid():
                # Get the committee that you want to change the active debate to and then set the active debate to be the new committees committee name.
                active_debate_committee = Committee.objects.get(pk=debate_form.cleaned_data['active_debate'])
                active_debate.active_debate = active_debate_committee.name
                # Save the new active debate
                active_debate.save()
                for committee in committees:
                    committee.next_subtopics.clear()
                # Send the user to the manage page
                messages.add_message(request, messages.SUCCESS, 'Active Debate Saved')
                return HttpResponseRedirect(reverse('statistics:runningorder', args=[session_id]))
            # You also have to create an empty/default instance of the "opposite" form, since we've got two on this page.
            round_form = ActiveRoundForm(max_rounds_array, {'session': session.name})
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
            debate_form = ActiveDebateForm(committees_array, {'session': session.name})

    # Otherwise, give the User some nice new forms.
    else:
        debate_form = ActiveDebateForm(committees_array, {'session': session.name})
        round_form = ActiveRoundForm(max_rounds_array, {'session': session.name})

    context = {'session': session, 'committees': committees, 'active': active, 'active_round': active_round,
               'debate_form': debate_form, 'round_form': round_form, 'no_footer': True}
    return check_authorization_and_render(request, 'statistics/runningorder.html', context, session)
