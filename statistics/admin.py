from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext as _
from django.conf.urls import url
from .models import *


class StatisticsAdminSite(admin.AdminSite):
    # Text to put at the end of each page's <title>.
    site_title = ugettext_lazy('Statistics Administration')

    # Text to put in each page's <h1> (and above login form).
    site_header = ugettext_lazy('Statistics Administration')

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy('Statistics Administration')


admin_site = StatisticsAdminSite()

#Setting up admin inlines for Committees and Suptopics, allows easy adding of committees in the "Session creation" page,
#and Subtopics in the "Comiitee creation" page
class CommitteeInline(admin.StackedInline):
    model = Committee
    extra = 2

class SubTopicInline(admin.TabularInline):
    model = SubTopic
    extra = 2

class TopicPlaceInline(admin.TabularInline):
    model = TopicPlace

#Setting up the session Admin
class SessionAdmin(admin.ModelAdmin):
    #The feild set groups for the "Create Session" page, shows groups of data for easy session creation
    fieldsets = [
        (None,                  {'fields': ['name', 'description', 'session_type', 'country', 'picture', 'admin_user', 'submission_user', 'email', 'website_link', 'resolution_link', 'facebook_link', 'twitter_link', 'picture_author', 'picture_author_link', 'picture_licence', 'picture_license_link']}),
        ('Date information',    {'fields': ['start_date', 'end_date']}),
        ('Session Settings',    {'fields': ['is_visible', 'session_statistics', 'max_rounds', 'voting_enabled', 'has_technical_problems']}),
        ('Gender Settings',     {'fields': ['gender_enabled', 'gender_number_female', 'gender_number_male', 'gender_number_other']})

    ]

    #The inline should be the CommitteeInline to make it easy to make committees straight away.
    inlines = [CommitteeInline]

    #What fields should be shown when the sessinons are displayed in a list
    list_display = ('name', 'country', 'session_type', 'start_date', 'end_date', 'is_visible', 'session_ongoing', 'session_statistics', 'admin_user', 'submission_user')

    #How the list should be sorted, here by session start date
    list_filter = ['start_date']

    search_fields = ['name', 'country']

class CommitteeAdmin(admin.ModelAdmin):
    #Fieldsets don't need to be set here as there isn't really anything above the ordinary that needs to be defined

    #The Subtopic Inline for the create committees page allows users to easily create and edit subtopics when editing committees
    inlines = [SubTopicInline]

    #What things should be displayed in the Committees list
    list_display = ('name', 'topic_text', 'session')

    list_filter = ['name']


class TopicPlaceTypeFilter(admin.SimpleListFilter):
    title = _('topic_place_type')
    parameter_name = 'topic_place_type'

    def lookups(self, request, model_admin):
      return TopicPlace.SUBCLASS_CHOICES

    def queryset(self, request, queryset):
      if self.value():
        return queryset.exclude(**{self.value(): None})
      return queryset


class TopicAdmin(admin.ModelAdmin):
    search_fields = ['text', 'type', 'area', 'difficulty']
    list_display = ('text', 'type', 'area')
    # inlines = [
    #     TopicPlaceInline
    # ]


class TopicPlaceAdmin(admin.ModelAdmin):
    list_display = [
        'topic',
        'topic_place_type'
    ]
    list_filter = [TopicPlaceTypeFilter]

    def get_queryset(self, request):
      return super(TopicPlaceAdmin, self).get_queryset(request).select_subclasses()

    def gender(self, obj):
        return obj._meta.verbose_name

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            Model = TopicPlace.SUBCLASS(request.GET.get('topic_place_type'))
        else:
            Model = obj.__class__

        # When we change the selected gender in the create form, we want to reload the page.
        RELOAD_PAGE = "window.location.search='?topic_place_type=' + this.value"
        # We should also grab all existing field values, and pass them as query string values.

        class ModelForm(forms.ModelForm):
            if not obj:
                gender = forms.ChoiceField(
                    choices=[('', _('Please select...'))] + TopicPlace.SUBCLASS_CHOICES,
                    widget=forms.Select(attrs={'onchange': RELOAD_PAGE})
                )

            class Meta:
                model = Model
                exclude = ()

        return ModelForm

    def get_fields(self, request, obj=None):
        # We want gender to be the first field.
        fields = super(TopicPlaceAdmin, self).get_fields(request, obj)

        if 'topic_place_type' in fields:
            fields.remove('topic_place_type')
            fields = ['topic_place_type'] + fields

        return fields

    def get_urls(self):
        # We want to install named urls that match the subclass ones, but bounce to the relevant
        # superclass ones (since they should be able to handle rendering the correct form).
        urls = super(TopicPlaceAdmin, self).get_urls()
        print(urls)
        existing = '{}_{}_'.format(self.model._meta.app_label, self.model._meta.model_name)
        subclass_urls = []
        # for name, model in TopicPlace.SUBCLASS_OBJECT_CHOICES.items():
        #     opts = model._meta
        #     replace = '{}_{}_'.format(opts.app_label, opts.model_name)
        #     subclass_urls.extend([
        #         url(pattern.regex.pattern, pattern.callback, name=pattern.name.replace(existing, replace))
        #         for pattern in urls if pattern.name
        #     ])

        return urls + subclass_urls


class SubTopicAdmin(admin.ModelAdmin):
    #Which things should be displayed in the subtopics list
    list_display = ('text', 'committee', 'session')


class ActiveDebateAdmin(admin.ModelAdmin):
    #Which things should be displayed in the active debate list
    list_display = ('active_debate', 'session')


class AnnouncementAdmin(admin.ModelAdmin):
    #Defines how an announcement should look like in the admin
    list_display = ('valid_until', 'announcement_type', 'content')


class ActiveRoundAdmin(admin.ModelAdmin):
    #Which things should be displayed in the active round list
    list_display =('active_round', 'session')


class PointAdmin(admin.ModelAdmin):
    #Which things should be displayed in the list of points, filtered by time
    list_display = ('timestamp', 'session', 'point_type', 'committee_by', 'active_debate', 'active_round')
    list_filter = ['timestamp']


class ContentPointAdmin(admin.ModelAdmin):
    #Which things should be displayed in the list of content points, filtered by time.
    list_display = ('timestamp', 'session', 'committee_by', 'active_debate', 'point_content', 'point_type')
    list_filter = ['timestamp']


class RunningOrderAdmin(admin.ModelAdmin):
    list_display = ('session', 'position', 'committee_by', 'point_type')
    list_filter = ['position']


class VoteAdmin(admin.ModelAdmin):
    #Which things should be displayed in the list of votes, filtered by time
    list_display = ('timestamp', 'session', 'committee_by', 'active_debate', 'in_favour', 'against', 'abstentions', 'absent', 'total_votes')
    list_filter = ['timestamp']


class GenderAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'gender', 'session', 'committee')
    list_filter = ['timestamp']

#Registering all the admin pages and the model for each admin page.
admin_site.register(Session, SessionAdmin)
admin_site.register(Committee, CommitteeAdmin)
admin_site.register(SubTopic, SubTopicAdmin)
admin_site.register(Topic, TopicAdmin)
admin_site.register(TopicPlace, TopicPlaceAdmin)
admin_site.register(ActiveDebate, ActiveDebateAdmin)
admin_site.register(Announcement, AnnouncementAdmin)
admin_site.register(ActiveRound, ActiveRoundAdmin)
admin_site.register(Point, PointAdmin)
admin_site.register(ContentPoint, ContentPointAdmin)
admin_site.register(RunningOrder, RunningOrderAdmin)
admin_site.register(Vote, VoteAdmin)
admin_site.register(Gender, GenderAdmin)
