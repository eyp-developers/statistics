from django.contrib.auth.decorators import login_required
from statisticscore.models import Session, Committee
from helpers import check_authorization_and_render


@login_required(login_url='/login/')
def overview(request, session_id):
    session = Session.objects.get(pk=session_id)
    committees = Committee.objects.filter(session=session).order_by('name')
    context = {'session': session, 'committees': committees}

    return check_authorization_and_render(request, 'statisticscore/overview.html',
                                          context, session)
