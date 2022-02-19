import json
from decimal import Decimal
from django.http import HttpResponse
from statisticscore.models import Session, Committee, Point, RunningOrder, Vote, \
                              ActiveDebate, ActiveRound
from statisticscore.forms.running_order import RunningOrderForm


def position(data, session, position=0):
    order = RunningOrder.objects.filter(session=session).order_by('position')
    count = order.count()
    if count == 0:
        return 1
    else:
        if data == 'P':
            return count + 1;
        elif data == 'DR':
            for point in order:
                point.position += 1
                point.save()
            return 1
        elif data == 'R':
            for point in order:
                point.position += -1
                point.save()
        elif data == 'up':
            if position > 1:
                point = order.get(position=position)
                above = order.get(position=(position-1))
                point.position += -1
                above.position += 1
                point.save()
                above.save()
        elif data == 'down':
            if position < RunningOrder.objects.filter(session=session).order_by('-position')[0].position:
                point = order.get(position=position)
                below = order.get(position=(position+1))
                point.position += 1
                below.position += -1
                point.save()
                below.save()
        else:
            for point in order:
                if point.position > data:
                    point.position += -1
                    point.save()

def runningorder_api(request, session_id):
    session = Session.objects.get(pk=session_id)
    active_debate = ActiveDebate.objects.get(session=session).active_debate
    active_round = ActiveRound.objects.get(session=session).active_round
    thisdata = {}
    if request.method == 'POST':
        if request.POST.get('action') == 'R':
            if Point.objects.filter(session=session).count() < 0:
                dr_subtopics = Point.objects.filter(session=session).order_by('-pk')[0].subtopics.all()
            else:
                dr_subtopics = []
            point = RunningOrder.objects.filter(session=session).order_by('position')[0]
            newpoint = Point(session = session,
                committee_by = point.committee_by,
                active_debate = active_debate,
                active_round = active_round,
                point_type = point.point_type
                )
            newpoint.save()
            if point.point_type == 'P':
                for s in point.committee_by.next_subtopics.all():
                    newpoint.subtopics.add(s)
            else:
                for s in dr_subtopics:
                    newpoint.subtopics.add(s)
            point.delete()
            position('R', session)

        elif request.POST.get('action') == 'U':
            point = Point.objects.filter(session=session).order_by('-pk')[0]
            r = RunningOrder(
                session = session,
                position = position('DR', session),
                committee_by = point.committee_by,
                point_type = point.point_type
            )
            r.save()
            point.delete()
        elif request.POST.get('action') == 'C':
            queue = RunningOrder.objects.filter(session=session)
            for point in queue:
                point.delete()
        elif request.POST.get('action') == 'delete':
            pos = int(request.POST.get('position'))
            point = RunningOrder.objects.filter(session=session).filter(position=pos)
            point.delete()
            position(pos, session)
        elif request.POST.get('action') == 'move':
            position(str(request.POST.get('direction')), session, int(request.POST.get('position')))
        else:
            form = RunningOrderForm({'by': int(request.POST.get('by')), 'point_type': str(request.POST.get('type'))})
            if form.is_valid():
                r = RunningOrder(session=session,
                    position=position(form.cleaned_data['point_type'], session),
                    committee_by=Committee.objects.get(pk=form.cleaned_data['by']),
                    point_type=form.cleaned_data['point_type']
                    )
                r.save()
    else:
        committees = Committee.objects.filter(session=session)
        session_points = Point.objects.filter(session=session)
        debate_points = session_points.filter(active_debate=active_debate)
        committees_array = []
        for committee in committees:
            committee_session_points = session_points.filter(committee_by=committee).count()
            committee_debate_points = debate_points.filter(committee_by=committee).count()
            if (debate_points.count() != 0) & (session_points.count() != 0):
                height = Decimal(75)+(Decimal(25)-(Decimal(15)*(Decimal(committee_debate_points)/Decimal(debate_points.count())))+(Decimal(10)*(Decimal(committee_session_points)/Decimal(session_points.count()))))
            else:
                height = 75
            subtopics_next_array = []
            for subtopic in committee.next_subtopics.all():
                thissubtopic = {
                'subtopic': subtopic.text,
                'color': subtopic.subtopic_color(),
                'text_color': subtopic.text_color()
                }
                subtopics_next_array.append(thissubtopic)
            thiscommittee = {
                'pk': committee.pk,
                'session_total': committee_session_points,
                'debate_total': committee_debate_points,
                'next_subtopics': subtopics_next_array,
                'height': round(height, 4)
            }
            committees_array.append(thiscommittee)
        thisdata['committees'] = committees_array
        last_three = session_points.order_by('-pk')[0:3]
        backlog_array = []
        backlog_position = -1
        for point in last_three:
            point_subtopics = []
            for subtopic in point.subtopics.all():
                thissubtopic = {
                'subtopic': subtopic.text,
                'color': subtopic.subtopic_color(),
                'text_color': subtopic.text_color()
                }
                point_subtopics.append(thissubtopic)
            thispoint = {
                'position': backlog_position,
                'by': point.committee_by.name,
                'on': point.active_debate,
                'round': point.active_round,
                'type': point.point_type,
                'subtopics': point_subtopics
            }
            backlog_position += -1
            backlog_array.append(thispoint)
        thisdata['backlog'] = backlog_array

        queue = RunningOrder.objects.filter(session=session).order_by('position')
        queue_array = []
        for point in queue:
            point_subtopics = []
            if point.point_type == 'P':
                for subtopic in point.committee_by.next_subtopics.all():
                    thissubtopic = {
                    'subtopic': subtopic.text,
                    'color': subtopic.subtopic_color(),
                    'text_color': subtopic.text_color()
                    }
                    point_subtopics.append(thissubtopic)
            else:
                for subtopic in last_three[0].subtopics.all():
                    thissubtopic = {
                    'subtopic': subtopic.text,
                    'color': subtopic.subtopic_color(),
                    'text_color': subtopic.text_color()
                    }
                    point_subtopics.append(thissubtopic)

            thispoint = {
                'position': point.position,
                'by': point.committee_by.name,
                'on': active_debate,
                'round': active_round,
                'type': point.point_type,
                'subtopics': point_subtopics
            }
            queue_array.append(thispoint)
        thisdata['queue'] = queue_array


    content_json = json.dumps(thisdata)

    return HttpResponse(content_json, content_type='json')
