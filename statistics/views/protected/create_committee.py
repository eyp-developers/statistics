import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from statistics.models import Session, Committee, SubTopic
from statistics.forms.committee import CommitteeForm
from helpers import check_authorization_and_render


@login_required(login_url='/login/')
def create_committee(request, session_id):
    session = Session.objects.get(pk=session_id)
    committees = Committee.objects.filter(session=session).order_by('name')
    session_subtopics = SubTopic.objects.filter(session=session)
    if request.method == 'POST':
        if request.POST.get('delete') == 'true':
            committee = Committee.objects.get(pk=request.POST.get('pk'))

            committee.delete()

            response_data = {}
            response_data['msg'] = 'Committee was deleted.'

            return HttpResponse(
                    json.dumps(response_data),
                    content_type="application/json"
            )
        else:
            pk = request.POST.get('pk')
            name = request.POST.get('name')
            topic = request.POST.get('topic')
            subtopics = json.loads(request.POST.get('subtopics'))

            response_data = {}
            form = CommitteeForm({'pk': pk, 'name': name, 'topic': topic})
            if form.is_valid():
                committee_exists = False
                for committee in committees:
                    if committee.pk == form.cleaned_data['pk']:
                        committee_exists = True

                if committee_exists:
                    c = committees.filter(pk=form.cleaned_data['pk'])[0]
                else:
                    c = Committee()

                c.session = session
                c.name = form.cleaned_data['name']
                c.topic = form.cleaned_data['topic']
                c.save()

                subtopics_pretty_array = []
                committee_subtopics = SubTopic.objects.filter(committee=c)
                committee_new_subtopics = []
                for subtopic in subtopics:
                    if subtopic['pk'] != '':
                        subtopic_pk = int(subtopic['pk'])
                    else:
                        subtopic_pk = ''
                    for committee_subtopic in committee_subtopics:
                        if committee_subtopic.pk == subtopic_pk:
                            subtopic_exists = True
                            break
                    else:
                        if subtopic['subtopic'] == 'General' and committee_subtopics.filter(text='General'):
                            subtopic_exists = True
                        else:
                            subtopic_exists = False

                    if subtopic_exists:
                        if subtopic['subtopic'] == 'General':
                            s = committee_subtopics.filter(text='General')[0]
                        else:
                            s = committee_subtopics.get(pk=subtopic['pk'])
                    else:
                        s = SubTopic()

                    s.session = session
                    s.committee = c
                    s.text = subtopic['subtopic']
                    s.save()
                    committee_new_subtopics.append(s)
                    subtopics_pretty_array.append(s.text)

                for subtopic in committee_subtopics:
                    if subtopic not in committee_new_subtopics:
                        subtopic.delete()

                response_data['pk'] = c.pk
                response_data['subtopics'] = ', '.join(subtopics_pretty_array)

                return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                )

            else:
                response_data['errors'] = form.errors
                return HttpResponse(
                        json.dumps(response_data),
                        content_type="application/json"
                )
    else:
        form = CommitteeForm()

    context = {'session': session, 'committees': committees, 'subtopics': session_subtopics, 'form': form}

    return check_authorization_and_render(request, 'statistics/session_add.html', context, session)
