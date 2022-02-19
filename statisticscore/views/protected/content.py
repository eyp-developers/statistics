from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statisticscore.models import Session, Committee, SubTopic, ActiveDebate, \
                                ActiveRound, ContentPoint
from statisticscore.forms.content import ContentForm
from helpers import check_authorization_and_render


@login_required(login_url='/login/')
def content(request, session_id, committee_id=None):
    session = Session.objects.get(pk=session_id)

    if committee_id:
        render_committee = Committee.objects.get(pk=committee_id)
        all_form = False
    else:
        render_committee = ''
        all_form = True

    active = ActiveDebate.objects.get(session_id=session_id).active_debate
    active_committee = Committee.objects.filter(session__pk=session_id).filter(name=active)

    committees = Committee.objects.filter(session__pk=session_id)
    committees_array = []
    # Here we make an array of committees that can be passed to the form
    for committee in committees:
        committees_array.append((committee.pk, committee.name), )

    if request.method == 'POST':

        form = ContentForm(request.POST)
        if form.is_valid():
            contentpoint = ContentPoint(session=Session.objects.filter(name=form.cleaned_data['session'])[0],
                                        committee_by=Committee.objects.filter(session__pk=session_id).filter(
                                            name=form.cleaned_data['committee'])[0],
                                        active_debate=form.cleaned_data['debate'],
                                        point_type=form.cleaned_data['point_type'],
                                        point_content=form.cleaned_data['content']
                                        )
            contentpoint.save()
            messages.add_message(request, messages.SUCCESS, 'Content Point Successfully Submitted')
            return HttpResponseRedirect(reverse('statisticscore:content', args=[session_id, committee_id]))
    else:
        if all_form:
            form = ContentForm({'session': session.name, 'committee': '', 'debate': active})
        else:
            form = ContentForm(
                    {'session': session.name, 'committee': render_committee.name, 'debate': active})

    if all_form:
        context = {'debate': active, 'session': session, 'form': form, 'committees': committees_array,
                   'all_form': all_form}
    else:
        context = {'debate': active, 'committee': render_committee, 'session': session, 'form': form,
                   'committees': committees_array, 'all_form': all_form}

    return check_authorization_and_render(request, 'statisticscore/content_form.html', context, session, False)
