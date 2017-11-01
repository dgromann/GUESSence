# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>
#
# Function: Generates the main objects (called models in Django) that are used in the main function of 
#			Django, the views

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.conf.global_settings import LANGUAGES

'''
Main game class used throughout the play
'''
class Game(models.Model):
	game_id = models.IntegerField(default=0)
	city_id = models.IntegerField(default=0)
	describer_id = models.IntegerField(default=0)
	guesser_id = models.IntegerField(default=0)
	start_time = models.DateTimeField(editable=False)
	end_time = models.DateTimeField(auto_now=False, blank=True, null=True)
	last_guess_time = models.DateTimeField(auto_now=False, blank=True, null=True)
	success = models.IntegerField(default=0)

'''
Class to allow for message exchange within a game
'''
class Message(models.Model):
	game = models.ForeignKey('Game', related_name='message')
	message = models.CharField(max_length=200)	
	game_role = models.CharField(max_length=200, default="NULL")
	handle = models.TextField()
	timestamp = models.DateTimeField(default=timezone.now, db_index=True)

'''
Class to ask user for further demographic information after five games
'''
class DemUser(models.Model):
	#Required line to be using Django users
	user = models.OneToOneField(User)

	first_name =  models.CharField(max_length=200)	
	last_name =  models.CharField(max_length=200)
	
	#Demographic info on user 
	GENDER_CHOICES =(('F', 'Female'),('M', 'Male'),)
	gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='F')
	AGE_CHOICES = (('12-17', '12 – 17'), ('18-24', '18 – 24'), ('25-34', '25 - 34'), ('35-44', '35 – 44'), ('45-54', '45 – 54'), ('55-64', '55 – 64'), ('65-74', '65 - 74'), ('75+', '75+'),)
	age = models.CharField(max_length=5, choices=AGE_CHOICES, default='25-34')
	first_language = models.CharField(max_length=7, choices=LANGUAGES, default="en")	
	residence = models.CharField(max_length=200)
	origin = models.CharField(max_length=200)

	def __unicode__(self):
		return self.user.username

'''
Auxiliary class to track and exchange device ID between frontend and backend
'''
class DemographicUser(models.Model):
	#Required line to be using Django users
	user = models.OneToOneField(User)
	deviceID = models.CharField(max_length=3800, default='0')

	def __unicode__(self):
		return self.user.username

'''
Auxiliary class to track hidden parameters across the game
'''
class CustomUser(models.Model):
	#Required line to be using Django users
	user = models.OneToOneField(User)

	#Additional attributes of the users 
	url_tracking = models.URLField(blank=True)
	number_games = models.IntegerField(default=0)
	number_success = models.IntegerField(default=0)
	score = models.FloatField(default=0)
	timeouts = models.FloatField(default=0)
	feedback = models.CharField(max_length=3800, default=0)
	demUser = models.BooleanField(default=False)
	reported = models.IntegerField(default=0)

	def __unicode__(self):
		return self.user.username

'''
Deprectaed class used in previous version of Web application with email activation link
'''
class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile') #1 to 1 link with Django User
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

'''
Class to handle city objects within the games
'''
class City(models.Model):
	city_id = models.IntegerField(default=0)
	city_name = models.CharField(max_length=200)
	country = models.CharField(max_length=200)
	latitude = models.DecimalField(max_digits=11, decimal_places=8)
	longitude = models.DecimalField(max_digits=11, decimal_places=8)
	tabooWords = models.CharField(max_length=200)
	number_played = models.IntegerField(default=0)

	def tabooWords_as_list(self):
		return self.tabooWords.split(';')
