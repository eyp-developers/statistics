from django.conf.urls import url

from views import auth, apis, public_views, protected_views

#The URLs are quite important to the GA Stats system, as there's a custom API and system for accessing various forms
#Sessions, Debates, Point Submit and Vote Submit pages are accessed using the id's of the session/committee.
#The six special ones are the api urls that the debate and session pages use for the live reloading to function, they're linked to custom views that output some pretty JSON output.

urlpatterns = [
    url(r'^$', public_views.home, name='home'),
    url(r'^login/$', auth.ga_login, name='login'),
    url(r'^logout/$', auth.ga_logout, name='logout'),
    url(r'^create_session/$', protected_views.create_session, name='create_session'),
    url(r'^welcome/(?P<session_id>[0-9]+)/$', protected_views.welcome, name='welcome'),
    url(r'^edit/(?P<session_id>[0-9]+)/$', protected_views.edit, name='edit'),
    url(r'^committees/(?P<session_id>[0-9]+)/$', protected_views.add, name='add'),
    url(r'^session/(?P<session_id>[0-9]+)/$', public_views.session, name='session'),
    url(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', public_views.debate, name='debate'),
    url(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', public_views.committee, name='committee'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', protected_views.point, name='point'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/thanks/$', protected_views.thanks, name='thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', protected_views.vote, name='vote'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/thanks/$', protected_views.vote_thanks, name='vote_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', protected_views.content, name='content'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/thanks/$', protected_views.content_thanks, name='content_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/$', protected_views.joint, name='joint'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/thanks/$', protected_views.joint_thanks, name='joint_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/manage/$', protected_views.manage, name='manage'),
    url(r'^api/session/(?P<session_id>[0-9]+)/$', apis.session_api, name='session_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', apis.debate_api, name='debate_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/$', apis.session_vote_api, name='session_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', apis.debate_vote_api, name='debate_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', apis.content_api, name='content_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/since/$', apis.content_latest_api, name='content_latest_api'),
]
