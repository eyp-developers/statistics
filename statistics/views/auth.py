
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from statistics.forms.login import LoginForm
from statistics.models import Session

def ga_login(request):
# This view is shown, when a user tries to view any protected page, but isn't logged in. After they log in, they'll be taken to the appropriate place.
    form = LoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(username=username,
                            password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                messages.add_message(request, messages.SUCCESS, 'Welcome ' + user.username + ', you have been logged in.')

                # The next line gets arguments from URLs like this http://stats.eyp.org/login/?next=/overview/9/
                next = request.GET.get("next")

                if next:
                    # Here we will redirect them to the page they came from when they were sent to the login page
                    return HttpResponseRedirect(next)

                elif Session.objects.filter(admin_user=request.user):
                    # If the user is an admin of a session, send them to their session's page
                    session = Session.objects.get(admin_user=request.user)
                    return HttpResponseRedirect(reverse('statistics:session', args = [session.pk]))

                elif Session.objects.filter(submission_user=request.user):
                    # If the user is a submission user for a session, send them to their session's page
                    session = Session.objects.get(submission_user=request.user)
                    return HttpResponseRedirect(reverse('statistics:session', args = [session.pk]))

                else: # If they didn't have a destionation in the URL and if they have no associated session, then send them to the home page
                    return HttpResponseRedirect(reverse('statistics:home'))

            else: # If their account is not active, tell them and let them try to log in using a different account
                messages.add_message(request, messages.ERROR, 'Your user account is not active. Please contact an administrator.')
                return HttpResponseRedirect(reverse('statistics:login'))

        else: # If the account / password combination does not exist, tell tham and let them try again
            messages.add_message(request, messages.ERROR, 'This username password combination does not exist.')
            return HttpResponseRedirect(reverse('statistics:login'))

    template = 'statistics/login.html'
    context = {'form': form}
    return render(request, template, context)


def ga_logout(request):
    # If the user visits /logout/ he will be logged out.

    logout(request)
    messages.add_message(request, messages.SUCCESS, 'You are now logged out.')
    return HttpResponseRedirect(reverse('statistics:home'))
