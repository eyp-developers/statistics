import sys
import csv
import urllib.request
import datetime
import codecs

from django.core.management.base import BaseCommand, CommandError
from statisticscore.models import Session, Committee, Topic, TopicPlace, HistoricTopicPlace
from statisticscore import countries

DOC_LINK = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQHPOM9M0nSZUh-2tupRJIPaDniQyK0tGVjmoEuxs2qBfi7kWpw1OIiB7SdD5_XQX7TUxHLQA_gjhkH/pub?gid=0&single=true&output=csv'

class Command(BaseCommand):
    def handle(self, *args, **options):
        doc_response = urllib.request.urlopen(DOC_LINK)
        rows = csv.reader(codecs.iterdecode(doc_response, 'utf-8'))
        csv_topics = self.getTopicsFromCSVRows(rows)
        self.stdout.write("CSV TOPICS " + str(len(csv_topics)))
        db_topics = Topic.objects.all()

        total_topics = len(csv_topics)
        existing_topics = 0
        new_topics = 0
        new_places = 0

        for csv_topic in csv_topics:
            # self.stdout.write("Importing", csv_topic)
            if db_topics.filter(text=csv_topic['text']).exists():
                existing_topics += 1
                stats_topic = db_topics.get(text=csv_topic['text'])
                stats_topic = self.updateTopicExtras(stats_topic, csv_topic)
            else:
                new_topics += 1
                stats_topic = self.makeNewTopic(csv_topic)

            if not self.placeAlreadyExists(stats_topic, csv_topic):
                new_places += 1
                place = self.makeNewPlace(stats_topic, csv_topic)

        self.stdout.write("Total topics " + str(total_topics))
        self.stdout.write("Already existed " + str(existing_topics))
        self.stdout.write("New Topics " + str(new_topics))
        self.stdout.write("New Places " + str(new_places))

    def firstLineValid(self, row):
        rules = [
            row[0] == 'Topic',
            row[1] == 'National Committee',
            row[2] == 'Type of session',
            row[3] == 'Year',
            row[4] == 'Committee',
            row[5] == 'Topic Area',
            row[6] == 'Type of topic question',
            row[7] == 'Difficulty',
        ]
        return all(rules)

    def getTopicsFromCSVRows(self, rows):
        topics = []
        firstLine = True
        for row in rows:
            if firstLine:
                if not self.firstLineValid(row):
                    self.stdout.write("The CSV was not formatted as expected! Cowardly exiting")
                    sys.exit()
                firstLine = False
                self.stdout.write("First row according to format")
                continue
            topic = {
                'text': row[0],
                'country': row[1],
                'session_type': row[2],
                'year': row[3],
                'committee': row[4].split(' ')[0],
                'area': row[5],
                'type': row[6],
                'difficulty': row[7]
            }
            topics.append(topic)
        return topics

    def getTopicType(self, type):
        if type == 'Creative':
            return 'CR'
        elif type == 'Conflict':
            return 'CF'
        elif type == 'Strategy':
            return 'ST'
        else:
            return None

    def getTopicDifficulty(self, type):
        if type == 'Easy':
            return 'E'
        elif type == 'Intermediate':
            return 'I'
        elif type == 'Hard':
            return 'H'
        else:
            return None

    def makeNewTopic(self, topic):
        text = topic['text']
        type = self.getTopicType(topic['type'])
        area = topic['area'] if topic['area'] != '' else None
        difficulty = self.getTopicDifficulty(topic['difficulty'])
        topic = Topic(text=text, type=type, area=area, difficulty=difficulty)
        topic.save()
        return topic

    def updateTopicExtras(self, stats_topic, csv_topic):
        type = self.getTopicType(csv_topic['type'])
        area = csv_topic['area'] if csv_topic['area'] != '' else None
        difficulty = self.getTopicDifficulty(csv_topic['difficulty'])

        if type is not None:
            stats_topic.type = type
        if area is not None:
            stats_topic.area = area
        if difficulty is not None:
            stats_topic.difficulty = difficulty

        stats_topic.save()
        return stats_topic

    def countryNamesMatch(self, c1, c2):
        if c1.startswith('The'):
            c1 = ' '.join(c1.split(' ')[1:])
        if c2.startswith('The'):
            c2 = ' '.join(c2.split(' ')[1:])

        if c1 == c2:
            return True

    def getShortTopicCountry(self, country_name):
        for country in countries.SESSION_COUNTRIES:
            if self.countryNamesMatch(country[1], country_name):
                return country[0]

        return None

    def placeAlreadyExists(self, stats_topic, csv_topic):
        for topic_place in stats_topic.topicplace_set.all():
            rules = [
                topic_place.session_type() == csv_topic['session_type'] or (topic_place.session_type() == None and csv_topic['session_type'] == ''),
                topic_place.committee_name() == csv_topic['committee'],
                str(topic_place.year()) == csv_topic['year'] or (topic_place.year() == None and csv_topic['year'] == ''),
                topic_place.country() == self.getShortTopicCountry(csv_topic['country']) or (topic_place.country() == None and csv_topic['country'] == '')
            ]
            if all(rules):
                return True

        return False


    def makeNewPlace(self, stats_topic, csv_topic):
        date = datetime.date(int(csv_topic['year']), 1, 1)
        country = self.getShortTopicCountry(csv_topic['country'])
        session_type = csv_topic['session_type'] if csv_topic['session_type'] != '' else None
        committee_name = csv_topic['committee']
        historic_place = HistoricTopicPlace(
                            topic=stats_topic,
                            historic_date=date,
                            historic_country=country,
                            historic_session_type=session_type,
                            historic_committee_name=committee_name
                        )
        historic_place.save()
        return historic_place

