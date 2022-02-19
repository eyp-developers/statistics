from django.utils import timezone
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from statisticscore.models import Session, Point, Vote, Announcement


def home(request):
    # The home page needs a list of the first few sessions ordered by the start date, then more pages with the rest of the sessions.
    latest_sessions_list = Session.objects.filter(is_visible=True).order_by('-start_date')

    # class Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)
    paginator = Paginator(latest_sessions_list, 12)

    # The next line gets arguments from URLs like this https://stats.eyp.org/?page=2
    page = request.GET.get("page")
    try:
        latest_sessions_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        latest_sessions_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        latest_sessions_list = paginator.page(paginator.num_pages)

    # In this array we will store all the sessions which had activity today
    active_sessions = []
    today = timezone.now().date()
    # We could check all sessions, but if a session is so old it's not on the front-page anymore, we won't show it's activity.
    # Therefore, using latest_sessions_list saves a lot of database queries
    # latest_sessions_list only contains the sessions which show on the current page, due to how it's modified through the paginator.
    # This also means, that if a user visits later pages, they won't see the current activity anymore, which makes sense, since they are probably not interested if they're looking for an older session
    # Since this check is still quite expensive on the database (minimum 36 queries per 12 sessions per page) we will skip this completely, if the user is not on the first page.
    if (not page) or (int(page) == 1):
        for session in latest_sessions_list:
            iteration_latest_activity = session.session_latest_activity()
            if (iteration_latest_activity != False) and (iteration_latest_activity.date() == today):
                active_sessions.append(session)

    # We want to show all announcements on the hompage which have not expired yet
    announcements = Announcement.objects.filter(valid_until__gte=timezone.now())

    context = {
        'latest_sessions_list': latest_sessions_list,
        'active_sessions': active_sessions,
        'announcements': announcements
    }

    user = request.user
    if user.get_username() and not user.is_superuser:
        for session in Session.objects.all():
            if user == session.admin_user:
                # This appends the two key pairs to the context dictionary
                context.update({
                    'admin_session': True,
                    'session': session,
                })

    return render(request, 'statisticscore/home.html', context)
