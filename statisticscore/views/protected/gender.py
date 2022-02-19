from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statisticscore.models import Session, Committee, SubTopic, ActiveDebate, Gender
from statisticscore.forms.gender import GenderForm
from helpers import check_authorization_and_render


@login_required(login_url='/login/')
def gender(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.filter(session_id=session_id)[0]
    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    for committee in committees:
        committees_array.append((committee.pk, committee.name),)

    if request.method == 'POST':

        gender_form = GenderForm(committees_array, request.POST)

        if gender_form.is_valid():
            committee = Committee.objects.get(pk=gender_form.cleaned_data['committee'])
            gender_point = Gender(committee=committee, gender=gender_form.cleaned_data['gender'])

            gender_point.save()

            # Then send the user a success message.
            messages.add_message(request, messages.SUCCESS, 'Gender Successfully Submitted')
            return HttpResponseRedirect(reverse('statisticscore:gender', args=[session_id]))
    else:
        gender_form = GenderForm(committees_array)

    content = {'session': session, 'committees': committees, 'active': active_debate, 'form': gender_form}

    return check_authorization_and_render(request, 'statisticscore/gender_form.html', content, session, False)
