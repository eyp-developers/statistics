import json
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from statisticscore.models import Session, Committee, SubTopic, Topic, StatisticsTopicPlace
from statisticscore.forms.committee import CommitteeForm
from helpers import check_authorization_and_render


def delete_committee(request):
    committee = Committee.objects.get(pk=request.POST.get('pk'))

    committee.delete()

    response_data = {}
    response_data['msg'] = 'Committee was deleted.'

    return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
    )


def get_committee(pk):
    if Committee.objects.filter(pk=pk).exists():
        return Committee.objects.get(pk=pk)
    else:
        return Committee()


def update_topic_text(committee, topic_text):
    committee.topic_text = topic_text
    old_topic = None
    committee.save()

    if Topic.objects.filter(text=topic_text).exists():
        topic = Topic.objects.get(text=topic_text)
    else:
        topic = Topic(text=topic_text)
        topic.save()

    if StatisticsTopicPlace.objects.filter(committee=committee).exists():
        stats_topic = committee.statisticstopicplace
        old_topic = stats_topic.topic
        topic.area = stats_topic.topic.area
        topic.type = stats_topic.topic.type
        topic.difficulty = stats_topic.topic.difficulty
        stats_topic.topic = topic
        stats_topic.save()
    else:
        stats_topic = StatisticsTopicPlace(topic=topic, committee=committee)
        stats_topic.save()

    if old_topic and not len(old_topic.topicplace_set.all()):
        old_topic.delete()


def edit_committee(request, session, committees):
    pk = request.POST.get('pk')
    name = request.POST.get('name')
    topic = request.POST.get('topic')
    subtopics = json.loads(request.POST.get('subtopics'))

    response_data = {}
    form = CommitteeForm({'pk': pk, 'name': name, 'topic': topic})
    if not form.is_valid():
        response_data['errors'] = form.errors
        return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
        )

    c = get_committee(form.cleaned_data['pk'])

    c.session = session
    c.name = form.cleaned_data['name']
    update_topic_text(c, form.cleaned_data['topic'])
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


@login_required(login_url='/login/')
def create_committee(request, session_id):
    session = Session.objects.get(pk=session_id)
    committees = Committee.objects.filter(session=session).order_by('name')
    session_subtopics = SubTopic.objects.filter(session=session)
    if request.method == 'POST':
        if request.POST.get('delete') == 'true':
            return delete_committee(request)
        else:
            return edit_committee(request, session, committees)
    else:
        form = CommitteeForm()

    context = {'session': session, 'committees': committees, 'subtopics': session_subtopics, 'form': form}

    return check_authorization_and_render(request, 'statisticscore/session_add.html', context, session)
