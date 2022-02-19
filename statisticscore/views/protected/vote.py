from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statisticscore.models import Session, Committee, ActiveDebate, Vote
from statisticscore.forms.vote import VoteForm
from helpers import check_authorization_and_render


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
    active_committee = Committee.objects.filter(session__pk=session_id).filter(name=active)

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.name), )

    # If the user is trying to submit something:
    if request.method == 'POST':
        # Create an instance of the form and populate it with data from the request.
        form = VoteForm(request.POST)

        # If the data in the form is valid
        if form.is_valid():
            # Then make a vote from the data in the form.
            vote = Vote(session=Session.objects.filter(
                    name=form.cleaned_data['session'])[0],
                        committee_by=Committee.objects.filter(session__pk=session_id).filter(
                            name=form.cleaned_data['committee'])[0],
                        active_debate=form.cleaned_data['debate'],
                        in_favour=form.cleaned_data['in_favour'],
                        against=form.cleaned_data['against'],
                        abstentions=form.cleaned_data['abstentions'],
                        absent=form.cleaned_data['absent']
                        )
            # Save the vote to the database.
            vote.save()
            # Then send the user a success message.
            messages.add_message(request, messages.SUCCESS, "Your Committee's Votes were successfully submitted")
            return HttpResponseRedirect(reverse('statisticscore:vote', args=[session_id, committee_id]))

    else:
        # Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        if all_form:
            form = VoteForm(
                    {'session': session.name, 'committee': '', 'debate': active, 'in_favour': 0, 'against': 0,
                     'abstentions': 0, 'absent': 0})
        else:
            form = VoteForm(
                    {'session': session.name, 'committee': render_committee.name, 'debate': active,
                     'in_favour': 0, 'against': 0, 'abstentions': 0, 'absent': 0})
    if all_form:
        context = {'session': session, 'debate': active, 'form': form, 'all_form': all_form,
                   'committees': committees_array}
    else:
        context = {'session': session, 'committee': render_committee, 'debate': active, 'form': form,
                   'all_form': all_form, 'committees': committees_array}

    return check_authorization_and_render(request, 'statisticscore/vote_form.html', context, session, False)
