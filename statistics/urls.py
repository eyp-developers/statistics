from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^session/(?P<session_id>[0-9]+)/$', views.session, name='session'),
    url(r'^session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', views.debate, name='debate'),
    url(r'^session/(?P<session_id>[0-9]+)/committee/(?P<committee_id>[0-9]+)/$', views.committee, name='committee'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/$', views.point, name='point'),
    url(r'^session/(?P<session_id>[0-9]+)/point/(?P<committee_id>[0-9]+)/thanks/$', views.thanks, name='thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/$', views.vote, name='vote'),
    url(r'^session/(?P<session_id>[0-9]+)/vote/(?P<committee_id>[0-9]+)/thanks/$', views.vote_thanks, name='vote_thanks'),
    url(r'^session/(?P<session_id>[0-9]+)/manage/$', views.manage, name='manage'),
    url(r'^api/session/(?P<session_id>[0-9]+)/$', views.session_api, name='session_api'),
    url(r'^api/session/(?P<session_id>[0-9]+)/debate/(?P<committee_id>[0-9]+)/$', views.debate_api, name='debate_api'),
]
