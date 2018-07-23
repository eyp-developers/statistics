from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statistics.models import Session, Committee, SubTopic, ActiveDebate, \
                              ActiveRound
from statistics.forms.running_order import PredictForm, PredictEditForm
from helpers import check_authorization_and_render

@login_required(login_url='/login/')
def predict(request, session_id, committee_id):
    session = Session.objects.get(pk=session_id)
    committee = Committee.objects.get(pk=committee_id)
    active_debate = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(name=active_debate)
    if active_committee:
        active_subtopics = SubTopic.objects.filter(committee=active_committee[0])
    else:
        active_subtopics = []
    subtopics_next_array = []
    subtopics_array = []
    for subtopic in active_subtopics:
        subtopics_array.append((subtopic.pk, subtopic.text), )
    # If the user is trying to submit data (method=POST), take a look at it
    if request.method == 'POST':

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
            messages.add_message(request, messages.SUCCESS, 'Your Point was successfully sent to the board')
            return HttpResponseRedirect(reverse('statistics:predict', args=[session_id, committee_id]))

    else:
        # Otherwise, if the user isn't trying to submit anything, set up a nice new form for the user.
        form = PredictForm(subtopics_array, {'session': session, 'committee': committee})

    for subtopic in committee.next_subtopics.all():
        subtopics_next_array.append(subtopic.text)
    edit_form = PredictEditForm()
    context = {'session': session, 'committee': committee, 'active_debate': active_debate, 'form': form,
               'edit_form': edit_form, 'next_subtopics': subtopics_next_array}

    return check_authorization_and_render(request, 'statistics/predict_form.html', context, session, False)
