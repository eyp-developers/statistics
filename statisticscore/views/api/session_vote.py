import json
from django.http import HttpResponse
from statisticscore.models import Committee, Point, Vote


def session_vote_api(request, session_id):
    #This is for returning the specific vote data from the vote API for the voting chart on the session page.

    #First we need all the committees registered for that session
    committees = Committee.objects.filter(session__id=session_id).order_by('name')
    #Then all the votes for that session
    votes = Vote.objects.filter(session_id=session_id)
    total_votes = 0
    total_in_favour = 0
    total_against = 0
    total_abstentions = 0
    total_absent = 0
    #Then a list to add committee names to
    committee_list = []

    #And lists for different vote types
    in_favour = []
    against = []
    abstentions = []
    absent = []

    #For each committee,
    for committee in committees:
        #Let c be the name
        c = committee.name

        #Append each newly made variable to our nice lists.
        committee_list.append(c)

        #Set the counter for each vote type to 0
        debate_in_favour = 0
        debate_against = 0
        debate_abstentions = 0
        debate_absent = 0

        #Filter votes by the current committee
        v = votes.filter(active_debate=committee)

        #For each vote in the new list of votes
        for vc in v:
            #Add that votes count to the total count
            debate_in_favour += vc.in_favour
            debate_against += vc.against
            debate_abstentions += vc.abstentions
            debate_absent += vc.absent

        #Then, append the totals to the full list.
        in_favour.append(debate_in_favour)
        against.append(debate_against)
        abstentions.append(debate_abstentions)
        absent.append(debate_absent)
        total_in_favour += debate_in_favour
        total_against += debate_against
        total_abstentions += debate_abstentions
        total_absent += debate_absent


    #Finally output the result as JSON
    total_votes = total_in_favour + total_against + total_abstentions + total_absent
    session_voting_json = json.dumps({
    'committees': committee_list,
    'in_favour': in_favour,
    'against': against,
    'abstentions': abstentions,
    'absent': absent,
    'total_votes': total_votes,
    'total_in_favour': total_in_favour,
    'total_against': total_against,
    'total_abstentions': total_abstentions,
    'total_absent': total_absent,
    })
    return HttpResponse(session_voting_json, content_type='json')
