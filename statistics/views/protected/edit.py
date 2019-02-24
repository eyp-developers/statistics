from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from statistics.models import Session, Committee
from statistics.forms.session_edit import SessionEditForm
from helpers import check_authorization_and_render


@login_required(login_url='/login/')
def edit(request, session_id):
    s = Session.objects.get(pk=session_id)
    # If the User is trying to edit the session
    if request.method == 'POST':
        # Fill an instance of the form with the request data.
        form = SessionEditForm(request.POST, request.FILES)
        # Check if the created form is a valid form.
        if form.is_valid():
            # We need to set up time varaibles for the start and end of sessions.
            # We do this by creating date objects and combining the date objects with time midnight
            t_start = form.cleaned_data['start_date']
            t_end = form.cleaned_data['end_date']
            start_date = datetime.combine(t_start, datetime.min.time())
            end_date = datetime.combine(t_end, datetime.min.time())

            s.name = form.cleaned_data['name']
            s.description = form.cleaned_data['description']
            s.session_type = form.cleaned_data['type']
            if form.cleaned_data['picture'] is not None:
                s.picture = form.cleaned_data['picture']
            s.picture_author = form.cleaned_data['picture_author']
            s.picture_author_link = form.cleaned_data['picture_author_link']
            s.picture_licence = form.cleaned_data['picture_license']
            s.picture_license_link = form.cleaned_data['picture_license_link']
            s.topic_overview_link = form.cleaned_data['topic_overviews']
            s.resolution_link = form.cleaned_data['resolutions']
            s.website_link = form.cleaned_data['website']
            s.facebook_link = form.cleaned_data['facebook']
            s.twitter_link = form.cleaned_data['twitter']
            s.email = form.cleaned_data['email']
            s.country = form.cleaned_data['country']
            s.start_date = start_date
            s.end_date = end_date
            s.session_statistics = form.cleaned_data['statistics']
            s.voting_enabled = form.cleaned_data['voting_enabled']
            s.gender_enabled = form.cleaned_data['gender_statistics']
            s.max_rounds = form.cleaned_data['max_rounds']
            s.is_visible = form.cleaned_data['is_visible']
            s.has_technical_problems = form.cleaned_data['technical_problems']
            if form.cleaned_data['number_female_participants'] is not None:
                s.gender_number_female = form.cleaned_data['number_female_participants']
            if form.cleaned_data['number_male_participants'] is not None:
                s.gender_number_male = form.cleaned_data['number_male_participants']
            if form.cleaned_data['number_other_participants'] is not None:
                s.gender_number_other = form.cleaned_data['number_other_participants']
            # Save the newly edited session
            s.save()

            messages.add_message(request, messages.SUCCESS, 'Session Updated')
            return HttpResponseRedirect(reverse('statistics:edit', args=[session_id]))

    else:
        session = s
        form = SessionEditForm({'name': s.name,
                                'description': s.description,
                                'type': s.session_type,
                                'email': s.email,
                                'country': s.country,
                                'picture': s.picture.url,
                                'picture_author': s.picture_author,
                                'picture_author_link': s.picture_author_link,
                                'picture_license': s.picture_licence,
                                'picture_license_link': s.picture_license_link,
                                'website': s.website_link,
                                'facebook': s.facebook_link,
                                'twitter': s.twitter_link,
                                'topic_overviews': s.topic_overview_link,
                                'resolutions': s.resolution_link,
                                'start_date': timezone.make_naive(s.start_date).strftime("%Y-%m-%d"),
                                'end_date': timezone.make_naive(s.end_date).strftime("%Y-%m-%d"),
                                'statistics': s.session_statistics,
                                'voting_enabled': s.voting_enabled,
                                'gender_statistics': s.gender_enabled,
                                'number_female_participants': s.gender_number_female,
                                'number_male_participants': s.gender_number_male,
                                'number_other_participants': s.gender_number_other,
                                'max_rounds': s.max_rounds,
                                'is_visible': s.is_visible,
                                'technical_problems': s.has_technical_problems})

    context = {'session': s, 'form': form}
    return check_authorization_and_render(request,
                                          'statistics/session_edit.html',
                                          context, s)
