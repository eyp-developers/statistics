import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from statistics import countries, session_types

class Session(models.Model):
    #Name of the session, eg. Izmir 2015
    session_name = models.CharField(max_length=100)

    #Description of the session, eg. The 78th International Session of the European Youth Parliament
    session_description = models.CharField(max_length=200)

    #Session size
    session_type = models.CharField(max_length=3, choices=session_types.SESSION_TYPES, default=session_types.REGIONAL_SESSION)

    #Session Picture, uploading an image to the stats platform.
    session_picture = models.ImageField(upload_to='session_pictures/')

    #We want a contact email so we can send friendly emails to people.
    session_email = models.EmailField()

    # The following links will be displayed on the sessions main page if a link is provided
    session_resolution_link = models.URLField(blank=True)

    session_website_link = models.URLField(blank=True)

    session_facebook_link = models.URLField(blank=True)

    session_twitter_link = models.URLField(blank=True)

    session_country = models.CharField(max_length=2, choices=countries.SESSION_COUNTRIES, default=countries.ALBANIA)

    #Date Options
    session_start_date = models.DateTimeField('start date')
    session_end_date = models.DateTimeField('end date')

    #Setting up statistic types
    STATISTICS = 'S'
    CONTENT = 'C'
    JOINTFORM = 'JF'
    SPLITFORM = 'SF'
    RUNNINGORDER = 'R'
    RUNNINGCONTENT = 'RC'
    STATISTIC_TYPES = (
        (STATISTICS, 'Statistics Only'),
        (CONTENT, 'Point Content Only'),
        (JOINTFORM, 'Joint Form Statistics'),
        (SPLITFORM, 'Split Form Statistics'),
        (RUNNINGORDER, 'Running Order Statistics'),
        (RUNNINGCONTENT, 'Running Order Statistics with Point Content')
    )
    #Making the statistics type a selectable option
    session_statistics = models.CharField(max_length=3, choices=STATISTIC_TYPES, default=JOINTFORM)

    #We want to define a color for the session that can be used when styling pages.
    #Depricated
    session_color = models.CharField(max_length=20)

    #Then we need a text color depending on if the committee color is light or dark.
    def session_text_color(self):
        if self.session_color() in ['cyan', 'light-green', 'lime', 'yellow', 'amber', 'orange']:
            return('black')
        else:
            return('white')

    #We want a boolean to define whether the session should be visible to the public or not.
    session_is_visible = models.BooleanField('is visible')

    #Enabling/Disabling Session Settings
    session_voting_enabled = models.BooleanField('session-wide voting enabled', default=True)
    session_gender_enabled = models.BooleanField('gender statistics enabled', default=False)
    session_max_rounds = models.PositiveSmallIntegerField(default=3)

    gender_number_female = models.IntegerField(blank=True, null=True)
    gender_number_male = models.IntegerField(blank=True, null=True)
    gender_number_other = models.IntegerField(blank=True, null=True)

    # If the session has had technical problems some data is probably missing. If this is activated a message will be shown to indidate this.
    session_has_technical_problems = models.BooleanField('session has technical problems', default=False)

    #Defining two users for the session. The Admin user who can alter active debates, change points etc. and the
    #submit user, which will be the login for everyone at any given session who wants to submit a point.
    session_admin_user = models.ForeignKey(User, related_name = 'session_admin', blank = True, null = True)
    session_submission_user = models.ForeignKey(User, related_name = 'session_submit', blank = True, null = True)

    #Definition of the session for admin lists
    def __unicode__(self):
        return unicode(self.session_name)

    #Definition of the session being ongoing or not at the moment, simply checks if the current time is in between the start time and the end time.
    def session_ongoing(self):
        return (self.session_start_date <= timezone.now() and self.session_end_date >= timezone.now())
    session_ongoing.admin_order_field = 'session_start_date'
    session_ongoing.boolean = True
    session_ongoing.short_description = 'Session Ongoing'


#Defining the Active Debate Class that tells a session which debate is ongoing.
class ActiveDebate(models.Model):
    session = models.ForeignKey(Session)
    active_debate = models.CharField(max_length=8, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.active_debate)

#Defining the Active Round which tells a session which round is currently active.
class ActiveRound(models.Model):
    session = models.ForeignKey(Session)
    active_round = models.PositiveSmallIntegerField(null=True, blank=True)

    def __int__(self):
        return unicode(self.active_round)


#Defining a committee, there should be several of these connected with each session.
class Committee(models.Model):
    #Which session the committee should be connected to
    session = models.ForeignKey(Session)

    #What the name of the committee is. This should be the acronym of the committee. Aka: AFCO, ENVI, ITRE II
    committee_name = models.CharField(max_length=8)

    #What the topic of the committee is, can be any length.
    committee_topic = models.TextField()

    next_subtopics = models.ManyToManyField('SubTopic', blank=True, related_name='next_subtopics+')

    #We want to define an automatic color for the committee in question, based on the list of material design colors.
    def committee_color(self):
        color_id = self.pk%17
        if color_id == 1:
            return('red')
        elif color_id == 2:
            return('green')
        elif color_id == 3:
            return('yellow')
        elif color_id == 4:
            return('blue')
        elif color_id == 5:
            return('purple')
        elif color_id == 6:
            return('light-green')
        elif color_id == 7:
            return('orange')
        elif color_id == 8:
            return('cyan')
        elif color_id == 9:
            return('pink')
        elif color_id == 10:
            return('lime')
        elif color_id == 11:
            return('deep-orange')
        elif color_id == 12:
            return('light-blue')
        elif color_id == 13:
            return('deep-purple')
        elif color_id == 14:
            return('amber')
        elif color_id == 15:
            return('teal')
        elif color_id == 16:
            return('indigo')
        else:
            return('blue-grey')

    #Then we need a text color depending on if the committee color is light or dark.
    def committee_text_color(self):
        if self.committee_color() in ['cyan', 'light-green', 'lime', 'yellow', 'amber', 'orange']:
            return('black')
        else:
            return('white')

    #Defining how the committee will be displayed in a list.
    def __unicode__(self):
        return unicode(self.committee_name)

#Defining subtopics of a committee, there should ideally be between 3 and 7 of these, plus a "general" subtopic.
class SubTopic(models.Model):
    #Which session the subtopic is connected to (to prevent dupicate problems)
    session = models.ForeignKey(Session, null=True, blank=True)

    #Which committee within the session the subtopic should be connected to.
    committee = models.ForeignKey(Committee, blank=True, null=True)

    #Name/Text of the subtopic. Should be short and catchy.
    subtopic_text = models.CharField(max_length=200, blank=True, null=True)

    #We want to define an automatic color for the committee in question, based on the list of material design colors.
    def subtopic_color(self):
        color_id = self.pk%17
        if color_id == 1:
            return('red')
        elif color_id == 2:
            return('green')
        elif color_id == 3:
            return('yellow')
        elif color_id == 4:
            return('blue')
        elif color_id == 5:
            return('purple')
        elif color_id == 6:
            return('light-green')
        elif color_id == 7:
            return('orange')
        elif color_id == 8:
            return('cyan')
        elif color_id == 9:
            return('pink')
        elif color_id == 10:
            return('lime')
        elif color_id == 11:
            return('deep-orange')
        elif color_id == 12:
            return('light-blue')
        elif color_id == 13:
            return('deep-purple')
        elif color_id == 14:
            return('amber')
        elif color_id == 15:
            return('teal')
        elif color_id == 16:
            return('indigo')
        else:
            return('blue-grey')

    #Then we need a text color depending on if the committee color is light or dark.
    def subtopic_text_color(self):
        if self.subtopic_color() in ['cyan', 'light-green', 'lime', 'yellow', 'amber', 'orange']:
            return('black')
        else:
            return('white')

    #Defining what should be displayed in the admin list, it should be the suptopic text.
    def __unicode__(self):
        return unicode(self.subtopic_text)


#Defining a Point, which is one peice of data that is submitted for every point of debate.
class Point(models.Model):
    #Which session the point should be connected to.
    session = models.ForeignKey(Session)

    #Timestamp of when the point was last updated.
    timestamp = models.DateTimeField(auto_now=True)

    #Which committee the point was by.
    committee_by = models.ForeignKey(Committee)

    #Which was the active debate at the time the point was made.
    active_debate = models.CharField(max_length=8, blank=True, null=True)

    #Which was the Active Round at the time the point was made.
    active_round = models.PositiveSmallIntegerField(null=True, blank=True)

    #Defining the two point types, Point and Direct Response, the default will be Point.
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )
    point_type = models.CharField(max_length=2, choices=POINT_TYPES, default=POINT)

    #Saying that many subtopics can be connected to this point.
    subtopics = models.ManyToManyField(SubTopic, blank=True)

    #Definition of the point in an admin list will be the point type, "P" or "DR"
    def __unicode__(self):
        return unicode(self.point_type)

#For the running order, we need to set up a queueing system we can access at any point.
class RunningOrder(models.Model):
    #The running order has to be affiliated with a certain session
    session = models.ForeignKey(Session)
    #and it needs a position
    position = models.PositiveSmallIntegerField()
    #then we need to know which committee it is that wants to make a point
    committee_by = models.ForeignKey(Committee)
    #Finally we need to know what kind of point it is.
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )
    point_type = models.CharField(max_length=2, choices=POINT_TYPES, default=POINT)

#Creating the second kind of point, the content point, which contains the text of a given point. Based on Wolfskaempfs GA Stats.
class ContentPoint(models.Model):
    #The ContentPoint also needs to be affiliated with a certain session and committee
    #(which committee it was made by and which debate was active) in the same way as the statistic points.
    session = models.ForeignKey(Session)
    committee_by = models.ForeignKey(Committee)
    active_debate = models.CharField(max_length=8)

    #It's also to have a timestamp of when the content point was last edited
    timestamp = models.DateTimeField(auto_now=True)

    #Then we need the actual point content, which is a simple TextField.
    point_content = models.TextField()

    #Defining the two point types, Point and Direct Response, the default will be Point.
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )
    point_type = models.CharField(max_length=2, choices=POINT_TYPES, default=POINT)

    #We can also add a definition for showing in admin panels etc.
    def __unicode__(self):
        return unicode(self.point_content)

#Defining the voting class, one "vote" is filled in for each voting committee on each topic.
class Vote(models.Model):
    #Which session the Vote should be connected to.
    session = models.ForeignKey(Session)

    #Timestamp of when the vote was last updated
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)

    #Which debate was active when the vote was submitted
    active_debate = models.CharField(max_length=8)

    #Which committee the vote was by
    committee_by = models.ForeignKey(Committee)

    #How many votes there were in favour
    in_favour = models.PositiveSmallIntegerField()

    #How many votes there were against
    against = models.PositiveSmallIntegerField()

    #How many abstentions there were
    abstentions = models.PositiveSmallIntegerField()

    #How many delegates were absent, very important so that the total amount of votes in the end
    #always displays the same number
    absent = models.PositiveSmallIntegerField()

    #Definition of the vote in admin lists should be the committee who voted
    def __unicode__(self):
        return unicode(self.committee_by)

    #The definition of the total votes, which is the sum of all the vote types.
    def total_votes(self):
        return (self.in_favour + self.against + self.abstentions + self.absent)
    total_votes.integer = True
    total_votes.short_description = 'Total Votes'

#Defining the gender class, which is an optional tracking aspect of GA stats shown on each sessions admin page
class Gender(models.Model):
    #The gender needs to be connected to a session, the committee that was active at the time and the gender

    committee = models.ForeignKey(Committee)

    def session(self):
        return self.committee.session

    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)

    FEMALE = 'F'
    MALE = 'M'
    OTHER = 'O'
    GENDERS = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
        (OTHER, 'Other')
    )
    gender = models.CharField(max_length=1, choices=GENDERS, default=FEMALE)

    #Finally we can add an admin definition
    def __unicode__(self):
        return unicode(self.gender)