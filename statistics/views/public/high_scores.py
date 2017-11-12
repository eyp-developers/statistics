from decimal import Decimal
from django.shortcuts import render
from statistics.models import Session, Point, Committee, Vote


def high_scores(request):

    most_votes = dict()
    most_in_favour = dict()
    most_against = dict()
    most_points = dict()
    most_drs = dict()
    most_points_in_debate = dict()
    most_drs_in_debate = dict()
    most_successful = dict()
    most_unsuccessful = dict()
    best_mpp = dict()
    stats = False

    for s in Session.objects.all():
        if Point.objects.all().filter(session=s).count() != 0:
            stats = True

        if s.is_visible and ((not s.has_technical_problems) and stats):
            total_votes = 0
            in_favour = 0
            against = 0
            abstentions = 0
            votes = Vote.objects.filter(session__id=s.pk)
            for vote in votes:
                in_favour += vote.in_favour
                against += vote.against
                abstentions += vote.abstentions
                total_votes += vote.total_votes()
                if in_favour != 0 and total_votes != 0 and against != 0:
                    percent_in_favour = (Decimal(in_favour) / Decimal(total_votes)) * 100
                    percent_against = (Decimal(against) / Decimal(total_votes)) * 100
                    most_in_favour[s.name] = percent_in_favour
                    most_against[s.name] = percent_against

            most_votes[s.name] = total_votes

            total_points = 0
            total_drs = 0
            total_successful = 0
            total_unsuccessful = 0
            committees = Committee.objects.filter(session=s)
            for c in committees:
                if c.voting_successful():
                    total_successful += 1
                else:
                    total_unsuccessful += 1

                points = c.num_points()
                drs = c.num_drs()

                total_points += points
                total_drs += drs
                most_points_in_debate[c.name + ', ' + s.name] = points
                most_drs_in_debate[c.name + ', ' + s.name] = drs

            most_points[s.name] = total_points
            most_drs[s.name] = total_drs
            most_successful[s.name] = total_successful
            most_unsuccessful[s.name] = total_unsuccessful
            if s.minutes_per_point() != 0:
                best_mpp[s.name] = s.minutes_per_point()

    five_most_votes = sorted(most_votes.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_in_favour = sorted(most_in_favour.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_against = sorted(most_against.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_points = sorted(most_points.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_drs = sorted(most_drs.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_points_in_debate = sorted(most_points_in_debate.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_drs_in_debate = sorted(most_drs_in_debate.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_successful = sorted(most_successful.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_most_unsuccessful = sorted(most_unsuccessful.items(), key=operator.itemgetter(1), reverse=True)[:5]
    five_best_mpp = sorted(best_mpp.items(), key=operator.itemgetter(1))[:5]

    context = {'top_voters': five_most_votes,
               'top_in_favour': five_most_in_favour,
               'top_against': five_most_against,
               'top_points': five_most_points,
               'top_drs': five_most_drs,
               'top_points_in_debate': five_most_points_in_debate,
               'top_drs_in_debate': five_most_drs_in_debate,
               'top_successful': five_most_successful,
               'top_unsuccessful': five_most_unsuccessful,
               'top_mpp': five_best_mpp,
               }
    return render(request, 'statistics/high_scores.html', context)
