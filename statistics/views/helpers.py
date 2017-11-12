from raven import Client
from django.conf import settings
from django.shortcuts import render

raven_client = Client(settings.RAVEN_CONFIG['dsn'])


# This is a central function. It replaces 'render' in cases where the user has to be authorized to view the page, not just authenticated.
def check_authorization_and_render(request, template, context, session, admin_only=True):
    if admin_only:  # This also refers to the session admin user AND any superuser
        if request.user == session.admin_user or request.user.is_superuser:
            return render(request, template, context)
        else:
            messages.add_message(request, messages.ERROR,
                                 'You are not authorized to view this page. You need to log in as the ' + session.name + ' admin.')
            return HttpResponseRedirect(reverse('statistics:login'))
    else:
        if request.user == session.admin_user or request.user == session.submission_user or request.user.is_superuser:
            return render(request, template, context)
        else:
            messages.add_message(request, messages.ERROR,
                                 'You are not authorized to view this page. You need to log in as the ' + session.name + ' admin.')
            return HttpResponseRedirect(reverse('statistics:login'))
