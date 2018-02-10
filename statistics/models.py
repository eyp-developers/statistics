import datetime
import time

from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from statistics import countries, session_types

# The following imports are used to process images for faster loading times
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToCover

SESSION_NAME_LEN=100
SESSION_DESCRIPTION_LEN=200
SESSION_AUTHOR_LEN=100
SESSION_LICENCE_LEN=100

TOPIC_AREA_LEN=200

COMMITTEE_NAME_MAX=8


class Session(models.Model):
    name = models.CharField(max_length=SESSION_NAME_LEN)
    description = models.CharField(max_length=SESSION_DESCRIPTION_LEN)

    #Session size
    session_type = models.CharField(max_length=3, choices=session_types.SESSION_TYPES, default=session_types.REGIONAL_SESSION)

    picture = models.ImageField(upload_to='session_pictures/')
    # Session picture used on front-page to help loading times
    picture_thumbnail = ImageSpecField(source='picture',
                                               processors=[ResizeToCover(400, 400)],
                                               format='JPEG',
                                               options={'quality': 80})
    # Session picture used on session page to help loading times and still acceptable image quality
    picture_large_fast = ImageSpecField(source='picture',
                                               processors=[ResizeToCover(1280, 400)],
                                               format='JPEG',
                                               options={'quality': 100})


    # Session picture author link allows users to credit photographers e.g. for Creative Commons content
    picture_author = models.CharField(max_length=SESSION_AUTHOR_LEN, blank=True)
    picture_author_link = models.URLField(blank=True)
    picture_licence = models.CharField(max_length=SESSION_LICENCE_LEN, blank=True)
    picture_license_link = models.URLField(blank=True)

    email = models.EmailField()

    # The following links will be displayed on the sessions main page if a link is provided
    resolution_link = models.URLField(blank=True)
    website_link = models.URLField(blank=True)
    facebook_link = models.URLField(blank=True)
    twitter_link = models.URLField(blank=True)
    country = models.CharField(max_length=2, choices=countries.SESSION_COUNTRIES, default=countries.ALBANIA)

    #Date Options
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

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
    session_statistics = models.CharField(max_length=5, choices=STATISTIC_TYPES, default=JOINTFORM)

    is_visible = models.BooleanField('is visible')

    voting_enabled = models.BooleanField('session-wide voting enabled', default=True)
    gender_enabled = models.BooleanField('gender statistics enabled', default=False)
    max_rounds = models.PositiveSmallIntegerField(default=3)

    gender_number_female = models.IntegerField(blank=True, null=True)
    gender_number_male = models.IntegerField(blank=True, null=True)
    gender_number_other = models.IntegerField(blank=True, null=True)

    # If the session has had technical problems some data is probably missing. If this is activated a message will be shown to indidate this.
    has_technical_problems = models.BooleanField('session has technical problems', default=False)

    #Defining two users for the session. The Admin user who can alter active debates, change points etc. and the
    #submit user, which will be the login for everyone at any given session who wants to submit a point.
    admin_user = models.ForeignKey(
                            User,
                            related_name='session_admin',
                            blank=True,
                            null=True,
                            on_delete=models.CASCADE
                        )

    submission_user = models.ForeignKey(
                                User,
                                related_name='session_submit',
                                blank=True,
                                null=True,
                                on_delete=models.CASCADE
                            )

    def __str__(self):
        return str(self.name)

    def session_ongoing(self):
        return (self.start_date <= timezone.now() and self.end_date >= timezone.now())
    session_ongoing.admin_order_field = 'start_date'
    session_ongoing.boolean = True
    session_ongoing.short_description = 'Session Ongoing'

    def session_latest_activity(self):
        """
        Returns date and time of the latest activity of the session. If there was never any activity, return 1972 as latest activity.
        """
        initialising_datetime = timezone.make_aware(datetime.datetime(1972, 1, 1, 2), timezone.get_default_timezone())
        latest_point = initialising_datetime
        latest_content = initialising_datetime
        latest_vote = initialising_datetime

        if Point.objects.filter(session=self):
            latest_point = Point.objects.filter(session=self).order_by('-timestamp')[0].timestamp
        if ContentPoint.objects.filter(session=self):
            latest_content = ContentPoint.objects.filter(session=self).order_by('-timestamp')[0].timestamp
        if Vote.objects.filter(session=self):
            latest_vote = Vote.objects.filter(session=self).order_by('-timestamp')[0].timestamp

        # This sorts the list of datetimes and the latest datetime is the third element of the list, which is saved to latest_activity
        latest_activity = sorted([latest_vote, latest_point, latest_content])[2]

        if latest_activity > initialising_datetime:
            return latest_activity
        else:
            return False

    def minutes_per_point(self):
        if self.session_statistics != 'C':
            all_points = Point.objects.filter(session=self).order_by('timestamp')
        else:
            all_points = ContentPoint.objects.filter(session=self).order_by('timestamp')

        if all_points.count() == 0:
            return 0

        total_points = all_points.count()
        first_point = all_points.first().timestamp
        latest_point = all_points.last().timestamp
        time_diff = latest_point - first_point
        minutes = (time_diff.days * 1440) + (time_diff.seconds / 60)

        return Decimal(minutes) / Decimal(total_points)

class ActiveDebate(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    active_debate = models.CharField(max_length=8, blank=True, null=True)

    def __str__(self):
        return str(self.active_debate)

class ActiveRound(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    active_round = models.PositiveSmallIntegerField(null=True, blank=True)

    def __int__(self):
        return str(self.active_round)


class Announcement(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    valid_until = models.DateTimeField()

    SUCCESS = 'alert-success'
    INFO = 'alert-info'
    WARNING = 'alert-warning'
    DANGER = 'alert-danger'
    ANNOUNCEMENT_TYPES = (
        (SUCCESS, 'Success'),
        (INFO, 'Info'),
        (WARNING, 'Warning'),
        (DANGER, 'Danger'),
    )
    announcement_type = models.CharField(max_length=15, choices=ANNOUNCEMENT_TYPES, default=INFO)

    def __str__(self):
        return str(self.announcement_type + self.content)


# Defining a committee, there should be several of these connected with each session.
class Committee(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    # Currently updating both until topics are stable
    topic_text = models.TextField()

    def get_topic(self):
        return self.statisticstopicplace.topic

    name = models.CharField(max_length=COMMITTEE_NAME_MAX)
    next_subtopics = models.ManyToManyField('SubTopic', blank=True, related_name='next_subtopics+')

    #We want to define an automatic color for the committee in question, based on the list of material design colors.
    def committee_color(self):
        color_id = self.pk % 17
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

    def voting_successful(self):
        votes = Vote.objects.filter(session=self.session).filter(active_debate=self.name)
        total = 0
        in_favour = 0
        absent = 0

        if len(votes) == 0:
            return False

        for vote in votes:
            total += vote.total_votes()
            in_favour += vote.in_favour
            absent += vote.absent

        return in_favour >= (total - absent) / 2

    def num_drs(self):
        points = Point.objects.filter(session=self.session).filter(active_debate=self.name)
        drs = 0

        for point in points:
            if point.point_type == 'DR':
                drs += 1

        return drs

    def num_points(self):
        points = Point.objects.filter(session=self.session).filter(active_debate=self.name)
        return len(points)

    def cleaned_name(self):
        """
        This returns the name of the committee without its enumeration to make it easier to use for categorisation
        """
        return self.name[:4]


    #Defining how the committee will be displayed in a list.
    def __str__(self):
        return str(self.name)


class Topic(models.Model):
    text = models.TextField(unique=True)

    CREATIVE = 'CR'
    CONFLICT = 'CF'
    STRATEGY = 'ST'
    TOPIC_TYPES = (
        (CREATIVE, 'Creative'),
        (CONFLICT, 'Conflict'),
        (STRATEGY, 'Strategy')
    )
    type = models.CharField(max_length=2, choices=TOPIC_TYPES, blank=True, null=True)

    area = models.CharField(max_length=TOPIC_AREA_LEN, blank=True, null=True)

    EASY = 'E'
    INTERMEDIATE = 'I'
    HARD = 'H'
    DIFFICULTIES = (
        (EASY, 'Easy'),
        (INTERMEDIATE, 'Intermediate'),
        (HARD, 'Hard')
    )
    difficulty = models.CharField(max_length=1, choices=DIFFICULTIES, blank=True, null=True)

    def __unicode__(self):
        return unicode(self.text)


class TopicPlace(models.Model):
    topic = models.ForeignKey(Topic, models.CASCADE)

    def child_method(self, method_name):
        try:
            method = getattr(self.statisticstopicplace, method_name)
            return method()
        except ObjectDoesNotExist:
            method = getattr(self.historictopicplace, method_name)
            return method()

    def session_type(self):
        return self.child_method('session_type')

    def committee_name(self):
        return self.child_method('committee_name')

    def year(self):
        return self.child_method('year')

    def country(self):
        return self.child_method('country')

    def __unicode__(self):
        return self.child_method('__unicode__')


class StatisticsTopicPlace(TopicPlace):
    committee = models.OneToOneField(Committee, models.SET_NULL, null=True)

    def session_name(self):
        return self.committee.session.name

    def session_type(self):
        return self.committee.session.session_type

    def committee_name(self):
        return self.committee.name.split(' ')[0]

    def year(self):
        return self.committee.session.end_date.year

    def country(self):
        return self.committee.session.country

    def __unicode__(self):
        return unicode(self.committee.session.name)


class HistoricTopicPlace(TopicPlace):
    historic_date = models.DateField(blank=True, null=True)
    historic_country = models.CharField(max_length=2, choices=countries.SESSION_COUNTRIES, blank=True, null=True)
    historic_session_type = models.CharField(max_length=3, choices=session_types.SESSION_TYPES, blank=True, null=True)
    historic_committee_name = models.CharField(max_length=COMMITTEE_NAME_MAX)

    def session_type(self):
        return self.historic_session_type

    def committee_name(self):
        return self.historic_committee_name

    def year(self):
        if self.historic_date is not None:
            return self.historic_date.year
        return None

    def country(self):
        return self.historic_country

    def __unicode__(self):
        string = ''
        if self.get_historic_country_display() is not None:
            string += self.get_historic_country_display()
        if self.historic_session_type is not None:
            if string != '':
                string += ' - '
            string += self.historic_session_typev
        if self.historic_committee_name is not None:
            if string != '':
                string += ' - '
            string += self.historic_committee_name
        if self.historic_date is not None:
            if string != '':
                string += ' - '
            string += str(self.historic_date.year)
        return unicode(string)

#Defining subtopics of a committee, there should ideally be between 3 and 7 of these, plus a "general" subtopic.
class SubTopic(models.Model):
    # Which session the subtopic is connected to (to prevent dupicate problems)
    # TODO: Remove this
    session = models.ForeignKey(Session, null=True, blank=True, on_delete=models.CASCADE)

    #Which committee within the session the subtopic should be connected to.
    committee = models.ForeignKey(Committee, blank=True, null=True, on_delete=models.CASCADE)

    #Name/Text of the subtopic. Should be short and catchy.
    text = models.CharField(max_length=200, blank=True, null=True)

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
    def text_color(self):
        if self.subtopic_color() in ['cyan', 'light-green', 'lime', 'yellow', 'amber', 'orange']:
            return('black')
        else:
            return('white')

    #Defining what should be displayed in the admin list, it should be the suptopic text.
    def __str__(self):
        return str(self.text)


#Defining a Point, which is one peice of data that is submitted for every point of debate.
class Point(models.Model):
    #Which session the point should be connected to.
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    #Timestamp of when the point was last updated.
    timestamp = models.DateTimeField(auto_now=True)

    #Which committee the point was by.
    committee_by = models.ForeignKey(Committee, on_delete=models.CASCADE)

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
    point_type = models.CharField(max_length=5, choices=POINT_TYPES, default=POINT)

    #Saying that many subtopics can be connected to this point.
    subtopics = models.ManyToManyField(SubTopic, blank=True)

    #Definition of the point in an admin list will be the point type, "P" or "DR"
    def __str__(self):
        return str(self.point_type)

#For the running order, we need to set up a queueing system we can access at any point.
class RunningOrder(models.Model):
    #The running order has to be affiliated with a certain session
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    #and it needs a position
    position = models.PositiveSmallIntegerField()
    #then we need to know which committee it is that wants to make a point
    committee_by = models.ForeignKey(Committee, on_delete=models.CASCADE)
    #Finally we need to know what kind of point it is.
    POINT = 'P'
    DIRECT_RESPONSE = 'DR'
    POINT_TYPES = (
        (POINT, 'Point'),
        (DIRECT_RESPONSE, 'Direct Response'),
    )
    point_type = models.CharField(max_length=5, choices=POINT_TYPES, default=POINT)

#Creating the second kind of point, the content point, which contains the text of a given point. Based on Wolfskaempfs GA Stats.
class ContentPoint(models.Model):
    #The ContentPoint also needs to be affiliated with a certain session and committee
    #(which committee it was made by and which debate was active) in the same way as the statistic points.
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    committee_by = models.ForeignKey(Committee, on_delete=models.CASCADE)
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
    point_type = models.CharField(max_length=5, choices=POINT_TYPES, default=POINT)

    #We can also add a definition for showing in admin panels etc.
    def __str__(self):
        return str(self.point_content)

#Defining the voting class, one "vote" is filled in for each voting committee on each topic.
class Vote(models.Model):
    #Which session the Vote should be connected to.
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    #Timestamp of when the vote was last updated
    timestamp = models.DateTimeField(auto_now=True)

    #Which debate was active when the vote was submitted
    active_debate = models.CharField(max_length=8)

    #Which committee the vote was by
    committee_by = models.ForeignKey(Committee, on_delete=models.CASCADE)

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
    def __str__(self):
        return str(self.committee_by)

    #The definition of the total votes, which is the sum of all the vote types.
    def total_votes(self):
        return (self.in_favour + self.against + self.abstentions + self.absent)
    total_votes.integer = True
    total_votes.short_description = 'Total Votes'

#Defining the gender class, which is an optional tracking aspect of GA stats shown on each sessions admin page
class Gender(models.Model):
    #The gender needs to be connected to a session, the committee that was active at the time and the gender

    committee = models.ForeignKey(Committee, on_delete=models.CASCADE)

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
    def __str__(self):
        return str(self.gender)
