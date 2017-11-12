from django.conf.urls import url
from statistics.views import *

session_urls = [
    url(r'^session/(?P<session_id>[0-9]+)/$', session, name='session'),
    url(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', debate, name='debate'),
    url(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', committee, name='committee'),
    url(r'^session/(?P<session_id>[0-9]+)/input/(?P<committee_id>[0-9]+)/$', predict, name='predict'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', point, name='point'),
    url(r'^session/(?P<session_id>[0-9]+)/point/all/$', point, name='point_all'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', vote, name='vote'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/all/$', vote, name='vote_all'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', content, name='content'),
    url(r'^session/(?P<session_id>[0-9]+)/content/all/$', content, name='content_all'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/$', joint, name='joint'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/all/$', joint, name='joint_all'),
]
