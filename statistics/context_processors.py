from django.conf import settings

def analytics(request):
    return {'analytics': settings.GOOGLE_ANALYTICS}