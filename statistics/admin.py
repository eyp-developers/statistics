from django.contrib import admin

from .models import Session, Committee, SubTopic, ActiveDebate, ActiveRound, Announcement, Point, ContentPoint, RunningOrder, Vote, Gender, Topic, TopicPlace

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

class CommitteeAdmin(admin.ModelAdmin):
    #Fieldsets don't need to be set here as there isn't really anything above the ordinary that needs to be defined

    #The Subtopic Inline for the create committees page allows users to easily create and edit subtopics when editing committees
    inlines = [SubTopicInline]

    #What things should be displayed in the Committees list
    list_display = ('name', 'topic_text', 'session')

    list_filter = ['name']


class TopicAdmin(admin.ModelAdmin):
    search_fields = ['text']
    list_display = ('text', 'type', 'area')
    inlines = [
        TopicPlaceInline
    ]


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
admin.site.register(Session, SessionAdmin)
admin.site.register(Committee, CommitteeAdmin)
admin.site.register(SubTopic, SubTopicAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(ActiveDebate, ActiveDebateAdmin)
admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(ActiveRound, ActiveRoundAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(ContentPoint, ContentPointAdmin)
admin.site.register(RunningOrder, RunningOrderAdmin)
admin.site.register(Vote, VoteAdmin)
admin.site.register(Gender, GenderAdmin)
