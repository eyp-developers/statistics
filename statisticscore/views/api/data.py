import json
from django.http import HttpResponse
from time import strftime
from statisticscore.models import Committee, Point, ContentPoint, Vote, SubTopic, Gender
from statisticscore.forms.point import PointEditForm
from statisticscore.forms.content import ContentEditForm
from statisticscore.forms.vote import VoteEditForm
from statisticscore.forms.running_order import PredictEditForm
from statisticscore.forms.delete import DeleteDataForm


def data_api(request, session_id):
    #For the 'offset' and 'count' arguments to work, we need to be able to tell the filter from which point and to which point to filter from.
    point_from = int(request.GET.get('offset'))
    point_to = int(request.GET.get('offset')) + int(request.GET.get('count'))
    #First we need all datapoints from that session
    json_datatype = str(request.GET.get('data_type'))
    if json_datatype == 'content':
        data = ContentPoint.objects.filter(session_id=session_id).order_by('-pk')[point_from:point_to]
        #We also need to count the amount of data points for the total
        total = ContentPoint.objects.filter(session_id=session_id).count()
    elif json_datatype == 'point':
        data = Point.objects.filter(session_id=session_id).order_by('-pk')[point_from:point_to]
        total = Point.objects.filter(session_id=session_id).count()
    elif json_datatype == 'vote':
        data = Vote.objects.filter(session_id=session_id).order_by('-pk')[point_from:point_to]
        total = Vote.objects.filter(session_id=session_id).count()
    elif json_datatype == 'predict':
        data = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).order_by('-pk')[point_from:point_to]
        total = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).count()
    elif json_datatype == 'gender':
        data = Gender.objects.filter(committee__session__pk=session_id).order_by('-pk')[point_from:point_to]
        total = Gender.objects.filter(committee__session__pk=session_id).count()


    #If there is no data, do nothing.
    if not data:
        content_json = json.dumps({
        'data': 'No data'
        })

    #But if we could find data
    else:
        #Create an empty array to put the data in
        data_list = []
        #Loop through the avaliable data
        for d in data:
            #For each data point, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            thisdata = {}
            thisdata['pk'] = d.pk
            thisdata['last_changed'] = d.timestamp.strftime("%H:%M")

            if json_datatype != 'gender':
                thisdata['committee_by'] = d.committee_by.name
                thisdata['active_debate'] = d.active_debate
                thisdata['committee_color'] = d.committee_by.committee_color()
                thisdata['committee_text_color'] = d.committee_by.committee_text_color()

            #For the different kinds of data points, we need to get different types of data.
            if json_datatype == 'content':
                thisdata['point_type'] = d.point_type
                thisdata['content'] = d.point_content
            elif json_datatype == 'point' or json_datatype == 'predict':
                thisdata['point_type'] = d.point_type
                thisdata['round_no'] = d.active_round
                subtopics_array = []
                for subtopic in d.subtopics.all():
                    subtopics_array.append(subtopic.text)
                thisdata['subtopics'] = ', '.join(subtopics_array)
            elif json_datatype == 'vote':
                thisdata['in_favour'] = d.in_favour
                thisdata['against'] = d.against
                thisdata['abstentions'] = d.abstentions
                thisdata['absent'] = d.absent
            elif json_datatype == 'gender':
                thisdata['gender'] = d.gender
                thisdata['committee'] = d.committee.name

            data_list.append(thisdata)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'datapoints': data_list,
        'totaldata': total
        })


    return HttpResponse(content_json, content_type='json')

def data_latest_api(request, session_id):
    #First we need all datapoints from that session that have a greater pk than *
    json_datatype = str(request.GET.get('data_type'))
    if json_datatype == 'content':
        data = ContentPoint.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        #We also need to count the amount of data points for the total
        total = ContentPoint.objects.filter(session_id=session_id).count()
    elif json_datatype == 'point':
        data = Point.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        total = Point.objects.filter(session_id=session_id).count()
    elif json_datatype == 'vote':
        data = Vote.objects.filter(session_id=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        total = Vote.objects.filter(session_id=session_id).count()
    elif json_datatype == 'predict':
        data = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        total = Point.objects.filter(session_id=session_id).filter(committee_by_id=int(request.GET.get('committee_id'))).count()
    elif json_datatype == 'gender':
        data = Gender.objects.filter(committee__session__pk=session_id).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
        total = Gender.objects.filter(committee__session__pk=session_id).count()

    #Create an empty array to put the contentpoints in
    data_list = []
    #If there are no points, do nothing.
    if not data:
        #Create a single object with out data.
        thisdata = {
        'pk': request.GET.get('pk')
        }

        data_list.append(thisdata)

        content_json = json.dumps({
        'datapoints': data_list,
        'totaldata': total
        })

    #But if we could find points
    else:
        #Loop through the avaliable contentpoints
        for d in data:
            #For each data point, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            thisdata = {}
            thisdata['pk'] = d.pk
            thisdata['last_changed'] = d.timestamp.strftime("%H:%M")

            if json_datatype != 'gender':
                thisdata['committee_by'] = d.committee_by.name
                thisdata['active_debate'] = d.active_debate
                thisdata['committee_color'] = d.committee_by.committee_color()
                thisdata['committee_text_color'] = d.committee_by.committee_text_color()

            #For the different kinds of data points, we need to get different types of data.
            if json_datatype == 'content':
                thisdata['point_type'] = d.point_type
                thisdata['content'] = d.point_content
            elif json_datatype == 'point' or json_datatype == 'predict':
                thisdata['point_type'] = d.point_type
                thisdata['round_no'] = d.active_round
                subtopics_array = []
                for subtopic in d.subtopics.all():
                    subtopics_array.append(subtopic.text)
                thisdata['subtopics'] = ', '.join(subtopics_array)
            elif json_datatype == 'vote':
                thisdata['in_favour'] = d.in_favour
                thisdata['against'] = d.against
                thisdata['abstentions'] = d.abstentions
                thisdata['absent'] = d.absent
            elif json_datatype == 'gender':
                thisdata['gender'] = d.gender
                thisdata['committee'] = d.committee.name

            data_list.append(thisdata)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'datapoints': data_list,
        'totaldata': total
        })


    return HttpResponse(content_json, content_type='json')

def data_pk_api(request):
    if request.method == 'POST':
        #If the user is trying to save/delete a piece of data.
        if request.POST.get('delete') == 'true':
            json_datatype = str(request.POST.get('data-type'))
            form = DeleteDataForm({'pk': int(request.POST.get('pk'))})
            if form.is_valid():
                if json_datatype == 'point':
                    d = Point.objects.get(pk=form.cleaned_data['pk'])
                if json_datatype == 'content':
                    d = ContentPoint.objects.get(pk=form.cleaned_data['pk'])
                if json_datatype == 'vote':
                    d = Vote.objects.get(pk=form.cleaned_data['pk'])
                if json_datatype == 'gender':
                    d = Gender.objects.get(pk=form.cleaned_data['pk'])
                d.delete()
                response_data = {}
                response_data['msg'] = 'Data deleted'

                response_json = json.dumps(response_data)

                return HttpResponse(response_json, content_type='json')

        else:
            if str(request.POST.get('data-type')) == 'predict':
                response_data = {}
                pk = int(request.POST.get('pk'))
                form = PredictEditForm({'pk': pk})
                subtopics = json.loads(request.POST.get('subtopics'))
                all_subtopics = json.loads(request.POST.get('all_subtopics'))

                if form.is_valid():
                    p = Point.objects.get(pk=form.cleaned_data['pk'])
                    p.subtopics.clear()

                    subtopics_array = []
                    for s in subtopics:
                        st = SubTopic.objects.get(pk=int(s.get('pk')))
                        p.subtopics.add(st)
                        subtopics_array.append(st.text)

                    response_data['pk'] = p.pk
                    response_data['last_changed'] = p.timestamp.strftime("%H:%M")
                    response_data['by'] = p.committee_by.name
                    response_data['debate'] = p.active_debate
                    response_data['round_no'] = p.active_round
                    response_data['point_type'] = p.point_type
                    response_data['subtopics'] = ', '.join(subtopics_array)
                    response_data['committee_color'] = p.committee_by.committee_color()
                    response_data['committee_text_color'] = p.committee_by.committee_text_color()

                    content_json = json.dumps(response_data)

                    return HttpResponse(content_json, content_type='json')
            else:
                #Get all our valiables according to what kind of data we're dealing with.
                response_data = {}
                json_datatype = str(request.POST.get('data-type'))
                session = int(request.POST.get('session'))
                pk = int(request.POST.get('pk'))
                committee = request.POST.get('committee')
                debate = request.POST.get('debate')
                if json_datatype == 'point':
                    round_no = int(request.POST.get('round_no'))
                    point_type = request.POST.get('point_type')
                    subtopics = json.loads(request.POST.get('subtopics'))
                    all_subtopics = json.loads(request.POST.get('all_subtopics'))

                    #Set up and instance of the Point Edit form.
                    form = PointEditForm({'pk': pk, 'session': session, 'committee': committee, 'debate': debate, 'round_no': round_no, 'point_type': point_type})

                    if form.is_valid():
                        #If the form is valid, get the Point and update it with our values.
                        p = Point.objects.get(pk=form.cleaned_data['pk'])

                        committee_by = Committee.objects.filter(session_id=form.cleaned_data['session']).filter(name=form.cleaned_data['committee'])[0]
                        p.committee_by = committee_by
                        p.active_debate = form.cleaned_data['debate']
                        p.active_round = form.cleaned_data['round_no']
                        p.point_type = form.cleaned_data['point_type']
                        p.save()
                        p.subtopics.clear()
                        subtopics_array = []
                        for s in subtopics:
                            st = SubTopic.objects.get(pk=int(s.get('pk')))
                            p.subtopics.add(st)
                            subtopics_array.append(st.text)

                        response_data['pk'] = p.pk
                        response_data['last_changed'] = p.timestamp.strftime("%H:%M")
                        response_data['by'] = p.committee_by.name
                        response_data['debate'] = p.active_debate
                        response_data['round_no'] = p.active_round
                        response_data['point_type'] = p.point_type
                        response_data['subtopics'] = ', '.join(subtopics_array)
                        response_data['committee_color'] = p.committee_by.committee_color()
                        response_data['committee_text_color'] = p.committee_by.committee_text_color()

                        content_json = json.dumps(response_data)

                        return HttpResponse(content_json, content_type='json')


                elif json_datatype == 'content':
                    point_type = request.POST.get('point_type')
                    content = request.POST.get('content')

                    form = ContentEditForm({'pk': pk, 'session': session, 'committee': committee, 'debate': debate, 'point_type': point_type, 'content': content})

                    if form.is_valid():
                        c = ContentPoint.objects.get(pk=form.cleaned_data['pk'])

                        committee_by = Committee.objects.filter(session_id=form.cleaned_data['session']).filter(name=form.cleaned_data['committee'])[0]
                        c.committee_by = committee_by
                        c.active_debate = form.cleaned_data['debate']
                        c.point_type = form.cleaned_data['point_type']
                        c.point_content = form.cleaned_data['content']
                        c.save()

                        response_data['pk'] = c.pk
                        response_data['last_changed'] = c.timestamp.strftime("%H:%M")
                        response_data['by'] = c.committee_by.name
                        response_data['debate'] = c.active_debate
                        response_data['point_type'] = c.point_type
                        response_data['content'] = c.point_content
                        response_data['committee_color'] = c.committee_by.committee_color()
                        response_data['committee_text_color'] = c.committee_by.committee_text_color()

                        content_json = json.dumps(response_data)

                        return HttpResponse(content_json, content_type='json')

                elif json_datatype == 'vote':
                    in_favour = request.POST.get('in_favour')
                    against = request.POST.get('against')
                    abstentions = request.POST.get('abstentions')
                    absent = request.POST.get('absent')

                    form = VoteEditForm({'pk': pk, 'session': session, 'committee': committee, 'debate': debate, 'in_favour': in_favour, 'against': against, 'abstentions': abstentions, 'absent': absent})

                    if form.is_valid():

                        v = Vote.objects.get(pk=form.cleaned_data['pk'])

                        committee_by = Committee.objects.filter(session_id=form.cleaned_data['session']).filter(name=form.cleaned_data['committee'])[0]

                        v.committee_by = committee_by
                        v.active_debate = form.cleaned_data['debate']
                        v.in_favour = form.cleaned_data['in_favour']
                        v.against = form.cleaned_data['against']
                        v.abstentions = form.cleaned_data['abstentions']
                        v.absent = form.cleaned_data['absent']
                        v.save()

                        response_data['pk'] = v.pk
                        response_data['last_changed'] = v.timestamp.strftime("%H:%M")
                        response_data['by'] = v.committee_by.name
                        response_data['debate'] = v.active_debate
                        response_data['in_favour'] = v.in_favour
                        response_data['against'] = v.against
                        response_data['abstentions'] = v.abstentions
                        response_data['absent'] = v.absent
                        response_data['committee_color'] = v.committee_by.committee_color()
                        response_data['committee_text_color'] = v.committee_by.committee_text_color()

                        content_json = json.dumps(response_data)

                        return HttpResponse(content_json, content_type='json')

        return HttpResponse(
            json.dumps({'opps': 'something went wrong'}),
            content_type='json'
        )
    else:
        json_datatype = str(request.GET.get('data_type'))
        pk = int(request.GET.get('pk'))
        thisdata = {}
        if json_datatype == 'content':
            data = ContentPoint.objects.get(pk=pk)
            thisdata['point_type'] = data.point_type
            thisdata['content'] = data.point_content
        elif json_datatype == 'point':
            data = Point.objects.get(pk=pk)
            thisdata['point_type'] = data.point_type
            thisdata['round_no'] = data.active_round
            #Getting the subtopics for a point
            subtopics_array = []
            for subtopic in data.subtopics.all():
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.text
                }
                subtopics_array.append(this_subtopic)
            thisdata['subtopics'] = subtopics_array
            #Getting all the subtopics avaliable for a certain point
            active_committee = Committee.objects.filter(session=data.session).filter(name=data.active_debate)[0]
            all_subtopics = SubTopic.objects.filter(committee=active_committee)
            all_subtopics_array = []
            for subtopic in all_subtopics:
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.text
                }
                all_subtopics_array.append(this_subtopic)
            thisdata['all_subtopics'] = all_subtopics_array
        elif json_datatype == 'predict':
            data = Point.objects.get(pk=pk)
            #Getting the subtopics for a point
            subtopics_array = []
            for subtopic in data.subtopics.all():
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.text
                }
                subtopics_array.append(this_subtopic)
            thisdata['subtopics'] = subtopics_array
            #Getting all the subtopics avaliable for a certain point
            active_committee = Committee.objects.filter(session=data.session).filter(name=data.active_debate)[0]
            all_subtopics = SubTopic.objects.filter(committee=active_committee)
            all_subtopics_array = []
            for subtopic in all_subtopics:
                this_subtopic = {
                'pk': subtopic.pk,
                'subtopic': subtopic.text
                }
                all_subtopics_array.append(this_subtopic)
            thisdata['all_subtopics'] = all_subtopics_array
        elif json_datatype == 'vote':
            data = Vote.objects.get(pk=pk)
            thisdata['in_favour'] = data.in_favour
            thisdata['against'] = data.against
            thisdata['abstentions'] = data.abstentions
            thisdata['absent'] = data.absent

        thisdata['pk'] = data.pk
        thisdata['committee_by'] = data.committee_by.name
        thisdata['active_debate'] = data.active_debate

        content_json = json.dumps(thisdata)

        return HttpResponse(content_json, content_type='json')
