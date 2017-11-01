# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>
#
# Function: Input forms that are displayed to the users

import datetime

from .models import CustomUser, Message, Profile, DemographicUser, DemUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.forms.utils import ErrorList
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from nocaptcha_recaptcha.fields import NoReCaptchaField
from django_countries import countries

'''
Main form for users to login after having registered - main registration is now handled by Firebase
'''
class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=200, label="")
    email = forms.EmailField(required=True, label="",max_length=200)
    password = forms.CharField(label="",max_length=200)
 
    class Meta:
        model = User
        fields = ('username', 'password', 'email')

'''
Form to acquire additional demographic information after five games
'''
class DemUserForm(forms.ModelForm):
    first_name = forms.CharField(required=False, max_length=30,label="", widget=forms.TextInput(attrs={'placeholder': 'first name','class':'form-control input-perso'}))
    last_name = forms.CharField(required=False, max_length=30, label="", widget=forms.TextInput(attrs={'placeholder': 'last name','class':'form-control input-perso'}))

    residence = forms.CharField(required=False, max_length=200,label="", widget=forms.TextInput(attrs={'placeholder': 'country of residence', 'class':'form-control'}))
    origin = forms.CharField(required=False, max_length=200,label="", widget=forms.TextInput(attrs={'placeholder': 'country of origin', 'class':'form-control'}))

    class Meta:
        model = DemUser
        fields = ('first_name', 'last_name', 'gender', 'age', 'first_language', 'residence', 'origin')
'''
Hidden form to track and exchange device ID between backend and frontend
'''
class DemographicUserForm(forms.ModelForm):
    deviceID = forms.CharField(max_length=3800, widget = forms.HiddenInput(attrs={'value': '0'}), required=False)

    class Meta:
        model = DemographicUser
        fields = ('deviceID',)

'''
Main form to allow for input of game messages
'''
class GameForm(forms.ModelForm):
	message = forms.CharField(max_length=200)

	class Meta: 
		model = Message
		fields = ('message',)
		widgets = {
            'message': forms.TextInput(
                attrs={'id': 'post-text', 'required': True, 'placeholder': 'Please enter your input...'}
            ),
        }

