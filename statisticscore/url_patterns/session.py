from django.urls import re_path
from statisticscore.views import *

session_urls = [
    re_path(r'^session/(?P<session_id>[0-9]+)/$', session, name='session'),
    re_path(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', debate, name='debate'),
    re_path(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', committee, name='committee'),
    re_path(r'^session/(?P<session_id>[0-9]+)/input/(?P<committee_id>[0-9]+)/$', predict, name='predict'),
    re_path(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', point, name='point'),
    re_path(r'^session/(?P<session_id>[0-9]+)/point/all/$', point, name='point_all'),
    re_path(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', vote, name='vote'),
    re_path(r'^session/(?P<session_id>[0-9]+)/vote/all/$', vote, name='vote_all'),
    re_path(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', content, name='content'),
    re_path(r'^session/(?P<session_id>[0-9]+)/content/all/$', content, name='content_all'),
    re_path(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/$', joint, name='joint'),
    re_path(r'^session/(?P<session_id>[0-9]+)/joint/all/$', joint, name='joint_all'),
]
