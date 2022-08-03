from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings

from statisticscore.views import *
from statisticscore.url_patterns.api import api_urls
from statisticscore.url_patterns.session import session_urls

# The URLs are quite important to the GA Stats system, as there's a custom API and system for accessing various forms
# Sessions, Debates, Point Submit and Vote Submit pages are accessed using the id's of the session/committee.
# The special ones are the api urls that the debate and session pages use for the live reloading to function,
# they're linked to custom views that output some pretty JSON output.

app_name = 'statisticscore'

urlpatterns = [
    re_path(r'^$', home, name='home'),
    re_path(r'^login/$', ga_login, name='login'),
    re_path(r'^logout/$', ga_logout, name='logout'),
    re_path(r'^get_started/$', get_started, name='get_started'),
    re_path(r'^changelog/$', changelog, name='changelog'),
    re_path(r'^create_session/$', create_session, name='create_session'),
    re_path(r'^highscores/$', high_scores, name='high_scores'),
    re_path(r'^topics/$', FilteredTopicsListView.as_view(), name='topics'),
    # path('topics/<int:pk>/edit', TopicUpdate.as_view(), name='update_topic'),
    # path('topics/<int:pk>/', TopicDetail.as_view(), name='topic_detail'),
    re_path(r'^overview/(?P<session_id>[0-9]+)/$', overview, name='overview'),
    re_path(r'^edit/(?P<session_id>[0-9]+)/$', edit, name='edit'),
    re_path(r'^committees/(?P<session_id>[0-9]+)/$', create_committee, name='create_committee'),
    re_path(r'^manage/(?P<session_id>[0-9]+)/$', manage, name='manage'),
    re_path(r'^gender/(?P<session_id>[0-9]+)/$', gender, name='gender'),
    re_path(r'^runningorder/(?P<session_id>[0-9]+)/$', runningorder, name='runningorder'),
]

urlpatterns += api_urls
urlpatterns += session_urls

if settings.IS_DEVELOPMENT:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
