from django.contrib import admin

from .models import Session, Committee, SubTopic, ActiveDebate, ActiveRound, Point, Vote

class CommitteeInline(admin.StackedInline):
    model = Committee
    extra = 2

class SubTopicInline(admin.TabularInline):
    model = SubTopic
    extra = 2

class SessionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,                  {'fields': ['session_name', 'session_description', 'session_country', 'session_picture', 'session_admin_user', 'session_submission_user']}),
        ('Date information',    {'fields': ['session_start_date', 'session_end_date']}),
        ('Session Settings',    {'fields': ['session_rounds_enabled', 'session_max_rounds', 'session_subtopics_enabled', 'session_voting_enabled']})
    ]
    inlines = [CommitteeInline]
    list_display = ('session_name', 'session_country', 'session_start_date', 'session_end_date', 'session_ongoing', 'session_admin_user', 'session_submission_user')
    list_filter = ['session_start_date']

class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('committee_name', 'session')
    inlines = [SubTopicInline]

class SubTopicAdmin(admin.ModelAdmin):
    list_display = ('subtopic_text', 'committee', 'session')

class ActiveDebateAdmin(admin.ModelAdmin):
    list_display = ('active_debate', 'session')

class ActiveRoundAdmin(admin.ModelAdmin):
    list_display =('active_round', 'session')

class PointAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'session', 'point_type', 'committee_by', 'active_debate', 'active_round')
    list_filter = ['timestamp']

class VoteAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'session', 'committee_by', 'active_debate', 'in_favour', 'against', 'abstentions', 'absent', 'total_votes')
    list_filter = ['timestamp']


admin.site.register(Session, SessionAdmin)
admin.site.register(Committee, CommitteeAdmin)
admin.site.register(SubTopic, SubTopicAdmin)
admin.site.register(ActiveDebate, ActiveDebateAdmin)
admin.site.register(ActiveRound, ActiveRoundAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Vote, VoteAdmin)
