"""eypstats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from statisticscore.admin import admin_site

urlpatterns = [
    url(r'^', include('statisticscore.urls')),
    url(r'^admin/', admin_site.urls),
]

handler404 = 'statisticscore.views.public_views.handler404'
handler500 = 'statisticscore.views.public_views.handler500'
