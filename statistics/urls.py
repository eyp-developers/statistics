from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings

from statistics.views import *
from url_patterns.api import api_urls
from url_patterns.session import session_urls

# The URLs are quite important to the GA Stats system, as there's a custom API and system for accessing various forms
# Sessions, Debates, Point Submit and Vote Submit pages are accessed using the id's of the session/committee.
# The special ones are the api urls that the debate and session pages use for the live reloading to function,
# they're linked to custom views that output some pretty JSON output.

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^login/$', ga_login, name='login'),
    url(r'^logout/$', ga_logout, name='logout'),
    url(r'^get_started/$', get_started, name='get_started'),
    url(r'^changelog/$', changelog, name='changelog'),
    url(r'^create_session/$', create_session, name='create_session'),
    url(r'^highscores/$', high_scores, name='high_scores'),
    url(r'^overview/(?P<session_id>[0-9]+)/$', overview, name='overview'),
    url(r'^edit/(?P<session_id>[0-9]+)/$', edit, name='edit'),
    url(r'^committees/(?P<session_id>[0-9]+)/$', create_committee, name='create_committee'),
    url(r'^manage/(?P<session_id>[0-9]+)/$', manage, name='manage'),
    url(r'^gender/(?P<session_id>[0-9]+)/$', gender, name='gender'),
    url(r'^runningorder/(?P<session_id>[0-9]+)/$', runningorder, name='runningorder'),
]

urlpatterns += api_urls
urlpatterns += session_urls

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
