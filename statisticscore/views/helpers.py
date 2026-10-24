from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


# This is a central function. It replaces 'render' in cases where the user has to be authorized to view the page, not just authenticated.
def check_authorization_and_render(request, template, context, session, admin_only=True):
    if admin_only:  # This also refers to the session admin user AND any superuser
        if request.user == session.admin_user or request.user.is_superuser:
            return render(request, template, context)
        else:
            messages.add_message(request, messages.ERROR,
                                 'You are not authorized to view this page. You need to log in as the ' + session.name + ' admin.')
            return HttpResponseRedirect(reverse('statisticscore:login'))
    else:
        if request.user == session.admin_user or request.user == session.submission_user or request.user.is_superuser:
            return render(request, template, context)
        else:
            messages.add_message(request, messages.ERROR,
                                 'You are not authorized to view this page. You need to log in as a ' + session.name + ' user.')
            return HttpResponseRedirect(reverse('statisticscore:login'))


@staff_member_required
def trigger_bugsink(request: HttpRequest):
    raise Exception("Raised Exception on purpose to send it to Bugsink")  # noqa: TRY002
