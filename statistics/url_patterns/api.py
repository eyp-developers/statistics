from django.conf.urls import url
from ..views import apis

api_urls = [
    url(r'^api/session/(?P<session_id>[0-9]+)/$', apis.session_api, name='session_api'),
    url(r'^api/runningorder/(?P<session_id>[0-9]+)/$', apis.runningorder_api, name='runningorder_api'),
    url(r'^api/committees/(?P<session_id>[0-9]+)/$', apis.committees_api, name='committees_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/data/$', apis.data_api, name='data_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/data/since/$', apis.data_latest_api, name='data_latest_api'),
    url(r'^api/pk_data/$', apis.data_pk_api, name='data_pk_api'),
    url(r'^api/active_debate/(?P<session_id>[0-9]+)/$', apis.active_debate_api, name='active_debate_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', apis.debate_api, name='debate_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/$', apis.session_vote_api, name='session_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', apis.debate_vote_api, name='debate_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', apis.content_api, name='content_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/since/$', apis.content_latest_api, name='content_latest_api'),
    url(r'^api/gender/(?P<session_id>[0-9]+)/$', apis.gender_api, name='gender_api'),
]
