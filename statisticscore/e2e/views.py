import datetime
import hmac
import json
from functools import wraps
from io import BytesIO

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from statisticscore.models import ActiveDebate, ActiveRound, Committee, ContentPoint, Gender, Point, Session, \
    StatisticsTopicPlace, SubTopic, Topic, Vote

DEFAULT_ADMIN_PASSWORD = 'e2e-admin-password'
DEFAULT_SUBMISSION_PASSWORD = 'e2e-submission-password'


def endpoints_enabled(request):
    if not getattr(settings, 'E2E_ENDPOINTS_ENABLED', False):
        return False
    expected = getattr(settings, 'E2E_TOKEN', '')
    given = request.META.get('HTTP_X_E2E_TOKEN', '')
    # An empty token setting never matches, so the endpoints can't be opened by accident.
    return bool(expected) and hmac.compare_digest(given.encode(), expected.encode())


def e2e_endpoint(*methods):
    """
    Hides the view behind the E2E flag and token (404 otherwise, so it looks like the URL doesn't exist),
    restricts it to the given HTTP methods and lets it skip CSRF, since it is called from the test runner.
    """
    def decorator(view):
        @csrf_exempt
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not endpoints_enabled(request):
                # Not raising Http404: the project's handler404 renders its page with status 200.
                return HttpResponseNotFound()
            if request.method not in methods:
                return JsonResponse({'error': 'Method not allowed'}, status=405)
            return view(request, *args, **kwargs)
        return wrapped
    return decorator


def read_json(request):
    if not request.body:
        return {}
    return json.loads(request.body)


def parse_date(value, default):
    date = datetime.date.fromisoformat(value) if value else default
    # Sessions created through the form start and end at midnight, so we do the same.
    return timezone.make_aware(datetime.datetime.combine(date, datetime.time.min))


def session_usernames(name):
    # This has to match the usernames create_session derives from the session name.
    lower_name = slugify(''.join(name.split()).lower())
    return lower_name + '_admin', lower_name


def test_picture():
    image = BytesIO()
    Image.new('RGB', (400, 300), color=(46, 71, 147)).save(image, 'JPEG')
    return ContentFile(image.getvalue(), 'e2e.jpg')


def add_committee(session, data):
    committee = Committee.objects.create(session=session, name=data['name'], topic_text=data.get('topic', ''))
    topic, _ = Topic.objects.get_or_create(text=committee.topic_text)
    StatisticsTopicPlace.objects.create(topic=topic, committee=committee)

    # Like the committees page, every committee gets a "General" subtopic first.
    subtopics = []
    for text in ['General'] + [s for s in data.get('subtopics', []) if s != 'General']:
        subtopic = SubTopic.objects.create(session=session, committee=committee, text=text)
        subtopics.append({'id': subtopic.pk, 'text': subtopic.text})

    return {'id': committee.pk, 'name': committee.name, 'subtopics': subtopics}


def session_state_json(session):
    return {
        'active_debate': ActiveDebate.objects.get(session=session).active_debate,
        'active_round': ActiveRound.objects.get(session=session).active_round,
        'visible': session.is_visible,
        'technical_problems': session.has_technical_problems,
        'voting_enabled': session.voting_enabled,
        'gender_enabled': session.gender_enabled,
    }


@e2e_endpoint('POST')
def create_session(request):
    data = read_json(request)
    name = data['name']
    admin_username, submission_username = session_usernames(name)

    if (Session.objects.filter(name=name).exists()
            or User.objects.filter(username__in=[admin_username, submission_username]).exists()):
        return JsonResponse({'error': 'Session with this name or a similar name already exists'}, status=409)

    admin_password = data.get('admin_password', DEFAULT_ADMIN_PASSWORD)
    submission_password = data.get('submission_password', DEFAULT_SUBMISSION_PASSWORD)
    today = timezone.localdate()

    with transaction.atomic():
        email = data.get('email', 'e2e@example.com')
        admin_user = User.objects.create_user(username=admin_username, email=email, password=admin_password)
        submission_user = User.objects.create_user(username=submission_username, email=email,
                                                   password=submission_password)

        session = Session(
            name=name,
            description=data.get('description', 'E2E test session'),
            session_type=data.get('type', 'RS'),
            email=email,
            country=data.get('country', 'DE'),
            start_date=parse_date(data.get('start_date'), today),
            end_date=parse_date(data.get('end_date'), today + datetime.timedelta(days=7)),
            session_statistics=data.get('mode', Session.JOINTFORM),
            is_visible=data.get('visible', False),
            voting_enabled=data.get('voting_enabled', True),
            gender_enabled=data.get('gender_enabled', False),
            max_rounds=data.get('max_rounds', 3),
            has_technical_problems=data.get('technical_problems', False),
            admin_user=admin_user,
            submission_user=submission_user,
        )
        session.picture = test_picture()
        session.save()

        committees = [add_committee(session, c) for c in data.get('committees', [])]

        ActiveDebate.objects.create(session=session, active_debate=data.get('active_debate', ''))
        ActiveRound.objects.create(session=session, active_round=data.get('active_round', 1))

    return JsonResponse({
        'id': session.pk,
        'name': session.name,
        'admin': {'username': admin_username, 'password': admin_password},
        'submission': {'username': submission_username, 'password': submission_password},
        'committees': committees,
    }, status=201)


@e2e_endpoint('DELETE')
def delete_session(request, session_id):
    session = Session.objects.filter(pk=session_id).first()
    if session is not None:
        users = [u for u in (session.admin_user, session.submission_user) if u is not None]
        # The picture file is left in place: a page rendering this session at the same moment would crash on a
        # missing file (the home page 500s when any listed picture is gone). The local server clears uploads on start.
        # Deleting the session cascades to its committees, points, votes and so on.
        session.delete()
        for user in users:
            user.delete()
    # Deleting something that is already gone is fine, so cleanup can always run.
    return HttpResponse(status=204)


@e2e_endpoint('POST')
def session_state(request, session_id):
    session = Session.objects.get(pk=session_id)
    data = read_json(request)

    if 'active_debate' in data:
        ActiveDebate.objects.filter(session=session).update(active_debate=data['active_debate'])
    if 'active_round' in data:
        ActiveRound.objects.filter(session=session).update(active_round=data['active_round'])

    fields = {'visible': 'is_visible', 'technical_problems': 'has_technical_problems',
              'voting_enabled': 'voting_enabled', 'gender_enabled': 'gender_enabled'}
    for key, field in fields.items():
        if key in data:
            setattr(session, field, data[key])
    session.save()

    return JsonResponse(session_state_json(session))


@e2e_endpoint('POST')
def session_data(request, session_id):
    """
    Adds points, content points, votes and gender entries in bulk. Committees and subtopics are given by name,
    the debate defaults to the active debate and the round to the active round. "minutes_ago" backdates an entry,
    since the models stamp themselves with the current time on save.
    """
    session = Session.objects.get(pk=session_id)
    data = read_json(request)
    committees = {c.name: c for c in Committee.objects.filter(session=session)}
    active_debate = ActiveDebate.objects.get(session=session).active_debate
    active_round = ActiveRound.objects.get(session=session).active_round
    created = {'points': [], 'content': [], 'votes': [], 'genders': []}

    def backdate(model, pk, entry):
        if 'minutes_ago' in entry:
            timestamp = timezone.now() - datetime.timedelta(minutes=entry['minutes_ago'])
            model.objects.filter(pk=pk).update(timestamp=timestamp)

    with transaction.atomic():
        for entry in data.get('points', []):
            debate = entry.get('debate', active_debate)
            point = Point.objects.create(session=session, committee_by=committees[entry['committee']],
                                         active_debate=debate, active_round=entry.get('round', active_round),
                                         point_type=entry.get('type', Point.POINT))
            subtopic_texts = entry.get('subtopics', ['General'])
            point.subtopics.set(SubTopic.objects.filter(committee=committees[debate], text__in=subtopic_texts))
            backdate(Point, point.pk, entry)
            created['points'].append(point.pk)

        for entry in data.get('content', []):
            content = ContentPoint.objects.create(session=session, committee_by=committees[entry['committee']],
                                                  active_debate=entry.get('debate', active_debate),
                                                  point_type=entry.get('type', ContentPoint.POINT),
                                                  point_content=entry['text'])
            backdate(ContentPoint, content.pk, entry)
            created['content'].append(content.pk)

        for entry in data.get('votes', []):
            vote = Vote.objects.create(session=session, committee_by=committees[entry['committee']],
                                       active_debate=entry.get('debate', active_debate),
                                       in_favour=entry.get('in_favour', 0), against=entry.get('against', 0),
                                       abstentions=entry.get('abstentions', 0), absent=entry.get('absent', 0))
            backdate(Vote, vote.pk, entry)
            created['votes'].append(vote.pk)

        for entry in data.get('genders', []):
            gender = Gender.objects.create(committee=committees[entry['committee']], gender=entry['gender'])
            backdate(Gender, gender.pk, entry)
            created['genders'].append(gender.pk)

    return JsonResponse(created, status=201)


@e2e_endpoint('POST')
def login_as(request):
    data = read_json(request)
    if 'username' in data:
        user = User.objects.get(username=data['username'])
    else:
        session = Session.objects.get(pk=data['session_id'])
        user = session.admin_user if data.get('role', 'admin') == 'admin' else session.submission_user

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return JsonResponse({'username': user.username})
