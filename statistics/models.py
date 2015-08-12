import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Session(models.Model):
    #Name of the session, eg. Izmir 2015
    session_name = models.CharField(max_length=100)

    #Description of the session, eg. The 78th International Session of the European Youth Parliament
    session_description = models.CharField(max_length=200)

    #Session Picture, currently a URL that links to a picture, can be taken from facebook, imgur etc. Should be changed to a file upload in future.
    session_picture = models.URLField()

    #All countries with EYP sessions recently (after googling)
    ALBANIA = 'AL'
    ARMENIA = 'AM'
    AUSTRIA = 'AT'
    AZERBAIJAN = 'AZ'
    BELARUS = 'BY'
    BELGIUM = 'BE'
    BOSNIA_AND_HERZEGOVINA = 'BA'
    CROATIA = 'HR'
    CYPRUS = 'CY'
    CZECH_REPUBLIC = 'CZ'
    DENMARK = 'DK'
    ESTONIA = 'EE'
    FINLAND = 'FI'
    FRANCE = 'FR'
    GEORGIA = 'GE'
    GERMANY = 'DE'
    GREECE = 'GR'
    HUNGARY = 'HU'
    IRELAND = 'IE'
    ITALY = 'IT'
    KOSOVO = 'XK'
    LATVIA = 'LV'
    LITHUANIA = 'LT'
    LUXEMBOURG = 'LU'
    NETHERLANDS = 'NL'
    NORWAY = 'NO'
    POLAND = 'PL'
    PORTUGAL = 'PT'
    ROMANIA = 'RO'
    RUSSIA = 'RU'
    SERBIA = 'RS'
    SLOVENIA = 'SI'
    SPAIN = 'ES'
    SWEDEN = 'SE'
    SWITZERLAND = 'CH'
    TURKEY = 'TR'
    UKRAINE = 'UA'
    UNITED_KINGDOM = 'GB'
    SESSION_COUNTRIES = (
        (ALBANIA, 'Albania'),
        (ARMENIA, 'Armenia'),
        (AUSTRIA, 'Austria'),
        (AZERBAIJAN, 'Azerbaijan'),
        (BELARUS, 'Belarus'),
        (BELGIUM, 'Belgium'),
        (BOSNIA_AND_HERZEGOVINA, 'Bosnia and Herzegovina'),
        (CROATIA, 'Croatia'),
        (CYPRUS, 'Cyprus'),
        (CZECH_REPUBLIC, 'Czech Republic'),
        (DENMARK, 'Denmark'),
        (ESTONIA, 'Estonia'),
        (FINLAND, 'Finland'),
        (FRANCE, 'France'),
        (GEORGIA, 'Georgia'),
        (GERMANY, 'Germany'),
        (GREECE, 'Greece'),
        (HUNGARY, 'Hungary'),
        (IRELAND, 'Ireland'),
        (ITALY, 'Italy'),
        (KOSOVO, 'Kosovo'),
        (LATVIA, 'Latvia'),
        (LITHUANIA, 'Lithuania'),
        (LUXEMBOURG, 'Luxembourg'),
        (NETHERLANDS, 'The Netherlands'),
        (NORWAY, 'Norway'),
        (POLAND, 'Poland'),
        (PORTUGAL, 'Portugal'),
        (ROMANIA, 'Romania'),
        (RUSSIA, 'Russia'),
        (SERBIA, 'Serbia'),
        (SLOVENIA, 'Slovenia'),
        (SPAIN, 'Spain'),
        (SWEDEN, 'Sweden'),
        (SWITZERLAND, 'Swizerland'),
        (TURKEY, 'Turkey'),
        (UKRAINE, 'Ukraine'),
        (UNITED_KINGDOM, 'The United Kingdom'),
    )
    session_country = models.CharField(max_length=2, choices=SESSION_COUNTRIES, default=ALBANIA)

    #Date Options
    session_start_date = models.DateTimeField('start date')
    session_end_date = models.DateTimeField('end date')

    #Enabling/Disabling Session Settings
    session_rounds_enabled = models.BooleanField('debate rounds enabled', default=True)
    session_subtopics_enabled = models.BooleanField('committee subtopics enabled', default=True)
    session_voting_enabled = models.BooleanField('session-wide voting enabled', default=True)
    session_max_rounds = models.PositiveSmallIntegerField(default=3)

    #Defining two users for the session. The Admin user who can alter active debates, change points etc. and the
    #submit user, which will be the login for everyone at any given session who wants to submit a point.
    session_admin_user = models.ForeignKey(User, related_name = 'session_admin', blank = True)
    session_submission_user = models.ForeignKey(User, related_name = 'session_submit', blank = True)

    #Definition of the session for admin lists
    def __str__(self):
        return self.session_name

    #Definition of the session being ongoing or not at the moment, simply checks if the current time is in between the start time and the end time.
    def session_ongoing(self):
        return (self.session_start_date <= timezone.now() and self.session_end_date >= timezone.now())
    session_ongoing.admin_order_field = 'session_start_date'
    session_ongoing.boolean = True
    session_ongoing.short_description = 'Session Ongoing'

#Defining the Active Debate Class that tells a session which debate is ongoing.
class ActiveDebate(models.Model):
    session = models.ForeignKey(Session)
    active_debate = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return self.active_debate

#Defining the Active Round which tells a session which round is currently active.
class ActiveRound(models.Model):
    session = models.ForeignKey(Session)
    active_round = models.PositiveSmallIntegerField(null=True, blank=True)

    def __int__(self):
        return self.active_round


#Defining a committee, there should be several of these connected with each session.
class Committee(models.Model):
    #Which session the committee should be connected to
    session = models.ForeignKey(Session)

    #What the name of the committee is. This should be the acronym of the committee. Aka: AFCO, ENVI, ITRE II
    committee_name = models.CharField(max_length=8)

    #What the topic of the committee is, can be any length.
    committee_topic = models.TextField()

    #Defining how the committee will be displayed in a list.
    def __str__(self):
        return str(self.committee_name)

#Defining subtopics of a committee, there should ideally be between 3 and 7 of these, plus a "general" subtopic.
class SubTopic(models.Model):
    #Which session the subtopic is connected to (to prevent dupicate problems)
    session = models.ForeignKey(Session, null=True, blank=True)

    #Which committee within the session the subtopic should be connected to.
    committee = models.ForeignKey(Committee, blank=True, null=True)

    #Name/Text of the subtopic. Should be short and catchy.
    subtopic_text = models.CharField(max_length=200, blank=True, null=True)

    #Defining what should be displayed in the admin list, it should be the suptopic text.
    def __str__(self):
        return self.subtopic_text

#Defining a Point, which is one peice of data that is submitted for every point of debate.
class Point(models.Model):
    #Which session the point should be connected to.
    session = models.ForeignKey(Session)

    #Timestamp of when the point was last updated.
    timestamp = models.DateTimeField(auto_now=True)

    #Which committee the point was by.
    committee_by = models.ForeignKey(Committee)

    #Which was the active debate at the time the point was made.
    active_debate = models.CharField(max_length=7, blank=True, null=True)

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
    def __str__(self):
        return self.point_type

#Defining the voting class, one "vote" is filled in for each voting committee on each topic.
class Vote(models.Model):
    #Which session the Vote should be connected to.
    session = models.ForeignKey(Session)

    #Timestamp of when the vote was last updated
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)

    #Which debate was active when the vote was submitted
    active_debate = models.CharField(max_length=7)

    #Which committee the vote was by
    committee_by = models.ForeignKey(Committee)

    #How many votes there were in favour
    in_favour = models.PositiveSmallIntegerField()

    #How many votes there were against
    against = models.PositiveSmallIntegerField()

    #How many abstentions there were
    abstentions = models.PositiveSmallIntegerField()

    #How many delegates were absent, very important so that the total amount of votes in the end always displays the same number
    absent = models.PositiveSmallIntegerField()

    #Definition of the vote in admin lists should be the committee who voted
    def __str__(self):
        return str(self.committee_by)

    #The definition of the total votes, which is the sum of all the vote types.
    def total_votes(self):
        return (self.in_favour + self.against + self.abstentions + self.absent)
    total_votes.integer = True
    total_votes.short_description = 'Total Votes'
