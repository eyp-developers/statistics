from django.conf.urls import url

from views import auth, apis, public_views, protected_views

#The URLs are quite important to the GA Stats system, as there's a custom API and system for accessing various forms
#Sessions, Debates, Point Submit and Vote Submit pages are accessed using the id's of the session/committee.
#The six special ones are the api urls that the debate and session pages use for the live reloading to function, they're linked to custom views that output some pretty JSON output.

urlpatterns = [
    url(r'^$', public_views.home, name='home'),
    url(r'^login/$', auth.ga_login, name='login'),
    url(r'^logout/$', auth.ga_logout, name='logout'),
    url(r'^create_session/$', public_views.create_session, name='create_session'),
    url(r'^overview/(?P<session_id>[0-9]+)/$', protected_views.welcome, name='welcome'),
    url(r'^edit/(?P<session_id>[0-9]+)/$', protected_views.edit, name='edit'),
    url(r'^committees/(?P<session_id>[0-9]+)/$', protected_views.add, name='add'),
    url(r'^manage/(?P<session_id>[0-9]+)/$', protected_views.manage, name='manage'),
    url(r'^runningorder/(?P<session_id>[0-9]+)/$', protected_views.runningorder, name='runningorder'),
    url(r'^session/(?P<session_id>[0-9]+)/$', public_views.session, name='session'),
    url(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', public_views.debate, name='debate'),
    url(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', public_views.committee, name='committee'),
    url(r'^session/(?P<session_id>[0-9]+)/predict/(?P<committee_id>[0-9]+)/$', protected_views.predict, name='predict'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', protected_views.point, name='point'),
    url(r'^session/(?P<session_id>[0-9]+)/point/all/$', protected_views.point, name='point_all'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', protected_views.vote, name='vote'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/all/$', protected_views.vote, name='vote_all'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', protected_views.content, name='content'),
    url(r'^session/(?P<session_id>[0-9]+)/content/all/$', protected_views.content, name='content_all'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/$', protected_views.joint, name='joint'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/all/$', protected_views.joint, name='joint_all'),
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
]
