from django.conf.urls import url

from . import views

#The URLs are quite important to the GA Stats system, as there's a custom API and system for accessing various forms
#Sessions, Debates, Point Submit and Vote Submit pages are accessed using the id's of the session/committee.
#The six special ones are the api urls that the debate and session pages use for the live reloading to function, they're linked to custom views that output some pretty JSON output.

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^create_session/$', views.create_session, name='create_session'),
    url(r'^welcome/(?P<session_id>[0-9]+)/$', views.welcome, name='welcome'),
    url(r'^edit/(?P<session_id>[0-9]+)/$', views.edit, name='edit'),
    url(r'^add/(?P<session_id>[0-9]+)/$', views.add, name='add'),
    url(r'^session/(?P<session_id>[0-9]+)/$', views.session, name='session'),
    url(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', views.debate, name='debate'),
    url(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', views.committee, name='committee'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', views.point, name='point'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/thanks/$', views.thanks, name='thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', views.vote, name='vote'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/thanks/$', views.vote_thanks, name='vote_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', views.content, name='content'),
    url(r'^session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/thanks/$', views.content_thanks, name='content_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/$', views.joint, name='joint'),
    url(r'^session/(?P<session_id>[0-9]+)/joint/(?P<committee_id>[0-9]+)/thanks/$', views.joint_thanks, name='joint_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/manage/$', views.manage, name='manage'),
    url(r'^api/session/(?P<session_id>[0-9]+)/$', views.session_api, name='session_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', views.debate_api, name='debate_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/$', views.session_vote_api, name='session_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', views.debate_vote_api, name='debate_vote_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/$', views.content_api, name='content_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/content/(?P<committee_id>[0-9]+)/since/$', views.content_latest_api, name='content_latest_api'),
]
