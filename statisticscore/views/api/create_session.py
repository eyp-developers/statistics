import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class SessionCreateRequest:
    def __init__(self, data):
        self.name = data.get('name')
        self.description = data.get('description')
        self.session_type = data.get('type')
        self.email = data.get('email')
        self.picture_author = data.get('picture_author')
        self.picture_author_link = data.get('picture_author_link')
        self.picture_license = data.get('picture_license')
        self.picture_license_link = data.get('picture_license_link')
        self.website_link = data.get('website')
        self.facebook_link = data.get('facebook')
        self.twitter_link = data.get('twitter')
        self.topic_overview_link = data.get('topic_overviews')
        self.resolution_link = data.get('resolutions')
        self.country = data.get('country')
        self.start_date = data.get('start_date')
        self.end_date = data.get('end_date')
        self.session_statistics = data.get('statistics')
        self.is_visible = False
        self.voting_enabled = data.get('voting_enabled') == 'True'
        self.gender_enabled = data.get('gender_statistics') == 'True'
        self.gender_number_female = data.get('number_female_participants')
        self.gender_number_male = data.get('number_male_participants')
        self.gender_number_other = data.get('number_other_participants')
        self.max_rounds = data.get('max_rounds')
        self.admin_user = data.get('admin_user')
        self.submission_user = data.get('submission_user')


@csrf_exempt
def create_session_api(request):
    # If the user is trying to create a session
    if request.method == 'POST':
        # Load JSON data from the request body.
        data = json.loads(request.body.decode('utf-8'))

        # Create a request object with the loaded JSON data.
        session_data = SessionCreateRequest(data)
        
        print(session_data)


        return JsonResponse({'status': 'success', 'session_id': 1})
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST method is accepted.'})
