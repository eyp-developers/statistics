from django.conf.urls import url
from ..views import public_views, protected_views

session_urls = [
    url(r'^session/(?P<session_id>[0-9]+)/$', public_views.session, name='session'),
    url(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', public_views.debate, name='debate'),
    url(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', public_views.committee, name='committee'),
    url(r'^session/(?P<session_id>[0-9]+)/input/(?P<committee_id>[0-9]+)/$', protected_views.predict, name='predict'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', protected_views.point, name='point'),
    url(r'^session/(?P<session_id>[0-9]+)/point/all/$', protected_views.point, name='point_all'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', protected_views.vote, name='vote'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/all/$', protected_views.vote, name='vote_all'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', protected_views.content, name='content'),
    url(r'^session/(?P<session_id>[0-9]+)/content/all/$', protected_views.content, name='content_all'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/$', protected_views.joint, name='joint'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/all/$', protected_views.joint, name='joint_all'),
]
