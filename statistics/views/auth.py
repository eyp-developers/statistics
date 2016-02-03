
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from ..forms import LoginForm


def ga_login(request):
# This view is shown, when a user tries to view the submit form, but isn't logged in. After they log in, they'll be taken to /submit/.
    form = LoginForm(request.POST or None)

    if form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(username=username,
                            password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                # The next line gets arguments from URLs like this http://stats.eyp.org/login/?next=/overview/9/
                next = request.GET.get("next")

                if next:
                    # Here we will redirect them to the page they came from when they were sent to the login page
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect(reverse('statistics:home'))
            else:
                messages.add_message(request, messages.ERROR, 'Your user account is not active. Please contact an administrator.')
                return HttpResponseRedirect(reverse('statistics:login'))
        else:
            messages.add_message(request, messages.ERROR, 'This username password combination does not exist.')
            return HttpResponseRedirect(reverse('statistics:login'))

    template = 'statistics/login.html'
    context = {'form': form}
    return render(request, template, context)


def ga_logout(request):
    # If the user visits /logout/ he will be logged out.

    logout(request)
    return HttpResponseRedirect(reverse('statistics:home'))
