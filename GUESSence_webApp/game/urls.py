# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>


"""taboo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from . import views
from django.contrib.auth.views import login
from django.contrib.auth.views import logout

app_name = 'game'

urlpatterns = [
    # /game/
    url(r'^$', views.index, name='index'),

    #Register URLs
    url(r'^register/$', views.register, name='register'),

    #Register URLs
    url(r'^disabled/$', views.disabled, name='disabled'),
    
    #Register URLs
    url(r'^demuser/(?P<game_id>[0-9]+)/$', views.demuser, name='demuser'),

    #Logout/game id
    url(r'^start/logout/(?P<game_id>[0-9]+)/$', views.logout_view, name='logout'),

    #/game/feedback/game_id
    url(r'^feedback/(?P<game_id>[0-9]+)/$', views.feedback, name='feedback'),

    #/game/reported/game_id
    url(r'^reported/(?P<game_id>[0-9]+)/$', views.reported, name='reported'),

    #/game/reported_redirect/game_id
    url(r'^reported_redirect/(?P<game_id>[0-9]+)/$', views.reported_redirect, name='reported_redirect'),
	
    #/game/feedback/game_id
    url(r'^provideFeedback/(?P<game_id>[0-9]+)/$', views.provideFeedback, name='provideFeedback'),

    #Instruction page
    url(r'^instructions/$', views.instructions, name='instructions'),

    #Starts the game
    url(r'^start/$', views.start, name='start'),

    #/game/start/success/
    url(r'^start/success/(?P<game_id>[0-9]+)/$', views.success, name='success'),
    
    #/game/timer/<game_id>
    url(r'^timer/(?P<game_id>[0-9]+)/$', views.timer, name='timer'),
    
    #/game/timeout/<game_id>
    url(r'^timeout/(?P<game_id>[0-9]+)/$', views.timeout, name='timeout'),

    #/game/players/
    url(r'^players/$', views.playersOnline, name='playersOnline'),

    #/game/scores/
    url(r'^scores/$', views.scores, name='scores'),

    #/game/<game_id>/
    url(r'^(?P<game_id>[0-9]+)/$', views.playing, name='playing'),

    #newgame
    url(r'^start/newgame/(?P<game_id>[0-9]+)/$', views.newgame, name='newgame'),

    #/game/update/<game_id>/
    url(r'^update/(?P<game_id>[0-9]+)/$', views.update, name='update'),

    #/game/player/<game_id>/
    url(r'^player/(?P<game_id>[0-9]+)/$', views.player, name='player'),

    #/game/warning/<game_id>/
    url(r'^warning/(?P<game_id>[0-9]+)/$', views.warning, name='warning'),

    #/game/unknownCity/<game_id>/
    url(r'^unknownCity/(?P<game_id>[0-9]+)/$', views.unknownCity, name='unknownCity'),
    
    #redirected back to previous game
    url(r'^recover/(?P<game_id>[0-9]+)/$', views.recover, name='recover'),

    #Unknown
    url(r'^unknown/(?P<game_id>[0-9]+)/$', views.unknown, name='unknown'),

    #/game/privacy/
    url(r'^privacy/$', views.privacy, name='privacy'),
] 

