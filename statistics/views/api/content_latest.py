import json
from django.http import HttpResponse
from statistics.models import Committee, Point, ContentPoint


def content_latest_api(request, session_id, committee_id):
    #We need the committee to filter by active debate name.
    committee = Committee.objects.get(pk=committee_id)
    #We need to get the contentpoints that have a pk greater than the "since" pk.
    contentpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.name).filter(pk__gt=request.GET.get('pk')).order_by('-pk')
    #We also need to count the points for the total
    totalpoints = ContentPoint.objects.filter(session_id=session_id).filter(active_debate=committee.name).count()
    #Create an empty array to put the contentpoints in
    contentpoint_list = []
    #If there are no points, do nothing.
    if not contentpoints:
        #Create a single object with out data.
        thispoint = {
        'pk': request.GET.get('pk')
        }

        contentpoint_list.append(thispoint)

        content_json = json.dumps({
        'contentpoints': contentpoint_list,
        'totalpoints': totalpoints
        })

    #But if we could find points
    else:
        #Loop through the avaliable contentpoints
        for p in contentpoints:
            #For each contentpoint, we need the id of the point, who the point was by, the kind of point, and the content of the point.
            committee_by = p.committee_by.name
            point_type = p.point_type
            content = p.point_content
            pk = p.pk
            committee_color = p.committee_by.committee_color()
            committee_text_color = p.committee_by.committee_text_color()

            #Create a single object with our data.
            thispoint = {
            'committee_by': committee_by,
            'point_type': point_type,
            'contentpoint': content,
            'pk': pk,
            'committee_color': committee_color,
            'committee_text_color': committee_text_color
            }

            contentpoint_list.append(thispoint)
        #Then we need to turn the list into JSON.
        content_json = json.dumps({
        'contentpoints': contentpoint_list
        })


    return HttpResponse(content_json, content_type='json')
