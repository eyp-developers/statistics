from django.conf.urls import url
from statisticscore.views import *

api_urls = [
    url(r'^api/session/(?P<session_id>[0-9]+)/$', session_api, name='session_api'),
    url(r'^api/runningorder/(?P<session_id>[0-9]+)/$', runningorder_api, name='runningorder_api'),
    url(r'^api/committees/(?P<session_id>[0-9]+)/$', committees_api, name='committees_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/data/$', data_api, name='data_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/data/since/$', data_latest_api, name='data_latest_api'),
    url(r'^api/pk_data/$', data_pk_api, name='data_pk_api'),
    url(r'^api/active_debate/(?P<session_id>[0-9]+)/$', active_debate_api, name='active_debate_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', debate_api, name='debate_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/$', session_vote_api, name='session_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', debate_vote_api, name='debate_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', content_api, name='content_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/since/$', content_latest_api, name='content_latest_api'),
    url(r'^api/gender/(?P<session_id>[0-9]+)/$', gender_api, name='gender_api'),
]
