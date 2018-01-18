from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from statistics.models import Session, Announcement, ActiveDebate, ActiveRound
from statistics.forms.session_create import SessionForm
from helpers import raven_client


def create_session(request):
    # If the user is trying to create a session
    if request.method == 'POST':
        # Fill an instance of a SessionForm with the request data.
        form = SessionForm(request.POST, request.FILES)
        if form.is_valid():
            lower_name = slugify(''.join(form.cleaned_data['name'].split()).lower())

            admin_username = lower_name + '_admin'
            submit_username = lower_name

            if (len(User.objects.filter(username=admin_username))
                    or len(User.objects.filter(username=submit_username))
                    or len(Session.objects.filter(name=form.cleaned_data['name']))):
                context = {'form': form, 'errors': ['Session with this name or a similar name already exists']}
                return render(request, 'statistics/session_create.html', context)

            # We need to set up time variables for the start and end of sessions.
            # We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            # We need to turn the voting 'True' and 'False' strings into actual booleans.
            voting = form.cleaned_data['voting_enabled'] == 'True'

            gender = form.cleaned_data['gender_statistics'] == 'True'

            # Creating a lowercase string with no spaces from the session name to use for usernames


            # Creating the Admin user
            admin_user = User.objects.create_user(username=admin_username,
                                                  email=form.cleaned_data['email'],
                                                  password=form.cleaned_data['admin_password'])


            user = authenticate(username=admin_user.username, password=form.cleaned_data['admin_password'])

            if user is not None:
                login(request, user)

            # Creating the Submit user
            submit_user = User.objects.create_user(username=submit_username,
                                                   email=form.cleaned_data['email'],
                                                   password=form.cleaned_data['submission_password'])


            # We need to create a session, active debate and active round.
            # We also need to create 2 new users for the session.
            session = Session(name=form.cleaned_data['name'],
                              description=form.cleaned_data['description'],
                              session_type=form.cleaned_data['type'],
                              email=form.cleaned_data['email'],
                              picture_author=form.cleaned_data['picture_author'],
                              picture_author_link=form.cleaned_data['picture_author_link'],
                              picture_licence=form.cleaned_data['picture_license'],
                              picture_license_link=form.cleaned_data['picture_license_link'],
                              website_link=form.cleaned_data['website'],
                              facebook_link=form.cleaned_data['facebook'],
                              twitter_link=form.cleaned_data['twitter'],
                              resolution_link=form.cleaned_data['resolution'],
                              country=form.cleaned_data['country'],
                              start_date=start_date,
                              end_date=end_date,
                              session_statistics=form.cleaned_data['statistics'],
                              is_visible=False, # When created, all sessions are initially hidden from the front page.
                              voting_enabled=voting,
                              gender_enabled=gender,
                              gender_number_female=form.cleaned_data['number_female_participants'],
                              gender_number_male=form.cleaned_data['number_male_participants'],
                              gender_number_other=form.cleaned_data['number_other_participants'],
                              max_rounds=form.cleaned_data['max_rounds'],
                              admin_user=admin_user,
                              submission_user=submit_user,
                              )
            session.picture = form.cleaned_data['picture']

            try:
                session.save()
            except Exception as e:
                # In cases of more serious errors, make sure to clean up
                raven_client.captureException()
                logout(request)
                admin_user.delete()
                submit_user.delete()
                context = {'form': form, 'errors': ['There was an error creating this session']}
                return render(request, 'statistics/session_create.html', context)

            active_debate = ActiveDebate(session=session, active_debate='')
            active_debate.save()
            active_round = ActiveRound(session=session, active_round=1)
            active_round.save()

            # Once we've done all that, lets say thanks for all that hard work and redirect the user to the new session.
            return HttpResponseRedirect(reverse('statistics:overview', args=[session.pk]))
    else:
        # Otherwise, create a nice new form for the user.
        form = SessionForm()

    announcements = Announcement.objects.filter(valid_until__gte=datetime.now())


    context = {'form': form, 'announcements': announcements}
    return render(request, 'statistics/session_create.html', context)
