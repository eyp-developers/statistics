from datetime import datetime
from django.shortcuts import render
from statisticscore.models import Session, Committee, ActiveDebate


def session(request, session_id):
    session = Session.objects.get(pk=session_id)
    session_committee_list = Committee.objects.filter(session=session).order_by('name')

    # We initialise the values of active_debate and active_debate_committee
    # with False, so that we don't get an error when we reference them in the
    # context dictionary
    context = {
        'session_committee_list': session_committee_list,
        'session': session,
        'active_debate': [],
        'active_debate_committee': [],
    }
    # This is the date and time of the latest activity of this session or False, if there was never any activity
    latest_activity = session.session_latest_activity()

    today = datetime.now().date()

    # It's important we only call date() on the result of session_latest_activity() if we know it's not False
    # This is why this part of the code is also inside the if latest_activity block
    # If it was false, we would get an error, because we can't call date() on a boolean
    if latest_activity and latest_activity.date() == today:
        active_debate = ActiveDebate.objects.get(session=session).active_debate

        context.update({
            'active_debate': active_debate,
            'active_debate_committee': Committee.objects.filter(session=session).get(name=active_debate),
        })

    return render(request, 'statisticscore/session.html', context)
