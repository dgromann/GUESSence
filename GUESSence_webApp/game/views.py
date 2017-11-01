# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>
#
# Function: Main controller of web application with main functionality

import random
import string
import hashlib
import datetime
import json

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .forms import UserForm, GameForm, DemographicUserForm, DemUserForm
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpRequest
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .models import Game, Message, City, Profile, CustomUser, DemographicUser, DemUser

from ipware.ip import get_real_ip
from unidecode import unidecode

from unidecode import unidecode
from game import namechecker as nm
from game import spellchecker 
from game import Truecaser 
from game import EvalTruecaser



import requests

'''
Redirects view to the page with privacy information
'''
def privacy(request):
	return render(request, 'game/privacy.html')

'''
This is a simple method that transfers the user to the main page. If the user comes
from a registered device, and they are still active in the database, render the last game they were playing.
If not, show the register page.
'''
def index(request):
	device_id = request.GET.get('deviceID', '')
	if device_id:
		try:
			demUser = DemographicUser.objects.get(deviceID=device_id)
			user_id=DemographicUser.objects.get(deviceID=device_id).user_id
			user = User.objects.get(id=user_id)
			if user.is_active:
				login(request,user)
				try:
					game = Game.objects.order_by('-start_time').filter(Q(describer_id=user.id) | Q(guesser_id=user.id), success=0)[0]
					chat = GameForm()
					city = City.objects.get(city_id=game.city_id)
					return render(request, 'game/game.html', {'game': game, 'city':city, 'chat':chat })
				except (Game.DoesNotExist,IndexError):
					return render(request, 'game/instructions.html', {'user': user, 'registered': True})
			else:
				user_form = UserForm()
				demographicuser_form = DemographicUserForm()
				return render(request, 'game/index.html', {'user_form':user_form, 'demographicuser_form':demographicuser_form})	
		except DemographicUser.DoesNotExist:
			user_form = UserForm()
			demographicuser_form = DemographicUserForm()
			return render(request, 'game/index.html', {'user_form':user_form, 'demographicuser_form':demographicuser_form})
	else:
		user_form = UserForm()
		demographicuser_form = DemographicUserForm()
		return render(request, 'game/index.html', {'user_form':user_form, 'demographicuser_form':demographicuser_form})

'''
This method receives the filled in form, stores the data in the database
and generates an activation key that is send per e-mail to the user as 
activation link. The key is stored in the DB as well
'''
@csrf_exempt 
def register(request):
	registered = False
	disabled = "y"
	user = User()

	if request.method == 'POST':
		data = json.loads(request.POST['data'])
		if not User.objects.filter(password=data['uid']).exists():
			user = User(username=data['displayName'], email=data['email'], password=data['uid'], last_login=timezone.now())

			if not User.objects.filter(username=data['displayName']).exists():
				user.save()
			else: 
				user.username = data['displayName']+"_"+str(random.randrange(1,227))
				user.save()

			demUser = DemographicUser()
			demUser.user = user
			demUser.deviceID = data['deviceID']
			demUser.save()

			ip = get_real_ip(request)
			trackUser = CustomUser()
			trackUser.user = user			
			trackUser.url_tracking = ip
			trackUser.save()

		else:
			user = User.objects.get(password=data['uid'])

			demUser = DemographicUser.objects.get(user_id=user)
			demUser.deviceID = data['deviceID']
			demUser.save()

			trackUser = CustomUser.objects.get(user_id=user)
			if trackUser.reported > 2:
				disabled = "x"

			if disabled == "y":
				game = Game.objects.filter(Q(describer_id=user.id) | Q(guesser_id=user.id))
				if len(game) == 0:
					disabled = "y"
				else:
					game = Game.objects.order_by('-start_time').filter(Q(describer_id=user.id) | Q(guesser_id=user.id))[0] 
					if game.game_id:
						disabled = game.game_id
				
	user.is_active = True
	authenticate(username=user.username, password=user.password)
	login(request, user)
	user.save()
	registered = True

	return HttpResponse({disabled})

'''
Redirects users that have been disabled
'''
def disabled(request):
	return render(request, 'game/disabled.html') 
		
'''
This method logs out users,delete the deviceID associated to them and stores the relevant data in the DB 
'''
def logout_view(request, game_id):
	user = User.objects.get(id=request.user.id)
	reported = False
	dem_user = DemographicUser.objects.get(user_id=request.user.id)

	user.is_active = False
	user.save()
	dem_user.deviceID = '0'
	dem_user.save()

	return render(request, 'game/logout.html', {'user': user, 'reported':reported})

'''
Method to redirect users who are logging out to the feedback page
'''
@csrf_exempt 
def feedback(request, game_id):
	game = Game.objects.get(game_id=game_id)
	message = Message()
	
	if request.user.id == game.describer_id or request.user.id == game.guesser_id:
		objs = Message.objects.filter(game_id=game.id)
		allMessages = ""

		for message in objs: 
			allMessages += message.message
		print(allMessages)
		if "The other user has logged out. Please click \"New Game\"!" not in allMessages:
			message1 = Message()
			message1.game_role = "GAME"
			message1.message = "The other user has logged out. Please click \"New Game\"!"
			message1.game = game
			message1.handle = 0
			message1.save()

	game.end_time = timezone.now()
	game.save() 

	'''Send a notification to the other user at this moment already since the other player has been 
	redirected to a different page and is not in the game anymore'''
	notify_user = 0
	if request.user.id == game.describer_id:
		notify_user = game.guesser_id
	else:
		notify_user = game.describer_id
	notify(notify_user,"The other player has logged out")
	
	return render(request, 'game/feedback.html', {'user': request.user, 'game':game})

'''
Stores the provided feedback 
'''
@csrf_exempt   
def provideFeedback(request, game_id):
	message = ""
	game = Game.objects.get(game_id=game_id)
	trackUser = CustomUser.objects.get(user_id=request.user.id)
	if request.method == "POST":
		message = request.POST['param']
		if trackUser:
			trackUser.feedback += " "+message
		else:
			trackUser.feedback = message
		trackUser.save()
	return HttpResponse({game.game_id})

'''
Users are redirected to this instruction page after having successfully registered/logged in
'''
def instructions(request):
	print(request.user)
	return render(request, 'game/instructions.html', {'user' : request.user})

'''
This method performs the input check for correct spelling and use of names, since 
proper nouns are not permitted in this game. If an incorrect spelling or a name is 
detected it returns a warning message to the user, either as popup or as message displayed
above the main message board.
'''
def warning(request, game_id):
	game = Game.objects.get(game_id=game_id)
	city = City.objects.get(city_id=game.city_id)
	objs = Message.objects.filter(game_id=game.id)
	#hints = Message.objects.filter(game_id=game.id,game_role="describer")
	size = len(objs)-1
	warning = None

	if len(objs) == 0:
		if request.user.id == game.guesser_id:
			warning = "Please wait for the describer to provide the first hint!"
		else: 
			warning = None


	if size >= 0: 
		if objs[size].game_role == "describer" and request.user.id == game.describer_id:
			warning = "Please wait for a guess after you submit a hint!"
		if objs[size].game_role == "guesser" and request.user.id == game.guesser_id: 
			warning = "Please wait for the next hint after you submit a guess!" 

	if not warning:	
		if request.method == "POST":
			message = request.POST['param']
			if message == "no clue":
				return HttpResponse({None})
			else:
				if request.user.id == game.describer_id:
					warning = nm.describerCheck(message, city.tabooWords)
				else:
					warning = nm.guesserCheck(message)
	return HttpResponse({warning})

'''
Method to come back to the game if the app is closed
'''
def recover(request, game_id):
	game = Game.objects.get(game_id=game_id)
	chat = GameForm()
	city = City.objects.get(city_id=game.city_id)
	messages = Message.objects.filter(game_id=game.id)
	for message in messages:
		if message.game_role == "GAME":
			game, city, chat = startGame(request)
			return render(request, 'game/game.html', {'game': game, 'city':city, 'chat':chat })
	return render(request, 'game/game.html', {'game': game, 'city':city, 'chat':chat })

'''
This is the main method for the game which generates a new game, assigns the city id to it, 
and assigns the entering user either the role describer or the role guesser. The first user in 
each game always has to be the guesser, the second the describer.
'''
def start(request):
	game, city, chat = startGame(request)
	return render(request, 'game/game.html', {'game': game, 'city':city, 'chat':chat })

'''This method starts the game and assigns players'''
def startGame(request):
	chat = GameForm()
	
	#Store the fact that this user starts a new game and adapt the score correspondingly
	trackUser = CustomUser.objects.get(user_id=request.user)
	trackUser.number_games += 1
	trackUser.score = trackUser.number_success+(0.1 * (trackUser.number_games-trackUser.number_success))-trackUser.timeouts	
	trackUser.save()

	#There are no games in the database and this is the very first game
	if not Game.objects.all(): 
		game = storeNewGame(request.user)
		city = City.objects.get(city_id=game.city_id)
		city.number_played += 1
		city.save()

	#There are some games in the db and the next one with an empty describer id needs to be 
	#retrieved
	else:
		games = Game.objects.filter(describer_id=0, end_time__isnull=True)
		
		if games:
			game = games[0]

			#Make sure the describer and the guesser cannot be the same player
			if game.guesser_id != request.user.id:
				game.describer_id = request.user.id
				city = City.objects.get(city_id=game.city_id)
				game.last_guess_time = timezone.now()
				game.save()
				notify(game.guesser_id,"Your game has started!")
			
			#If the current player already is a guesser in an open game 
			#the player needs to be assigned to a new game
			else:
	 			game = storeNewGame(request.user)
	 			city = City.objects.get(city_id=game.city_id)
	 			city.number_played += 1
	 			city.save()
	 			notify(request.user.id,"Your game has started!")
		else:
	 		game = storeNewGame(request.user)
	 		city = City.objects.get(city_id=game.city_id)
	 		city.number_played += 1
	 		city.save()
	 		notify(request.user.id,"Your game has started!")	
	return game, city, chat

'''
This method is called when one of the players hit "New Game". It redirects the one who hit the 
button to a new game and informs the other one that his partner has left the game.
'''
def newgame(request, game_id):
	timeout = False
	game = Game.objects.get(game_id=game_id)
	game.end_time = timezone.now()
	game.save()
	trackUser = CustomUser.objects.get(user_id=request.user)
	numberGames = trackUser.number_games
	done = trackUser.demUser
	
	if numberGames == 5 and done == False: 
		dem_user_form = DemUserForm()
		trackUser.demUser = True
		trackUser.save()
		return render(request, 'game/demographicUser.html', {'game': game, 'dem_user_form': dem_user_form, 'done': done })
	
	else:
		city = City.objects.get(city_id=game.city_id)
		objs = Message.objects.filter(game_id=game.id)
		allMessages = ""

		for message in objs: 
			if message.message == "Timeout!":
				timeout = True
			allMessages += message.message
		if "The other player has left the game. Please click \"New GAME\"!" not in allMessages:
			msg = Message()
			msg.message = "The other player has left the game. Please click \"New GAME\"!"
			msg.handle = 0
			msg.game_role = "GAME"
			msg.game = game 
			msg.save()

		if timeout == False:
			if game.describer_id == request.user.id:
				notify(game.guesser_id,"The other player has left the game")
			else:
				notify(game.describer_id,"The other player has left the game")
		game, city, chat = startGame(request)
		return render(request, 'game/game.html', {'game': game, 'city':city, 'chat':chat })

'''
Utility method to add additional metadata on the user in the DB
'''
def demuser(request, game_id):
	done = False
	game = Game.objects.get(game_id=game_id) 
	if request.method == 'POST':
		dem_user_form = DemUserForm(data=request.POST)
		user = User.objects.get(id=request.user.id)
		obj = dem_user_form.save(commit=False)
		obj.user = user
		obj.save()
		done = True

	dem_user_form = DemUserForm()
			
	return render(request, 'game/demographicUser.html', {'game': game, 'dem_user_form': dem_user_form, 'done': done})

'''
This method starts a new game without writing the success or game record into the players DB entries - the players
call this method when the describer clicks the "Unknown City" button
'''
def unknownCity(request, game_id):
	chat = GameForm()
	city = City()
	game = Game.objects.get(game_id=game_id)
	game.end_time = timezone.now()
	game.save()
	
	allMessages = ""
	objs = Message.objects.filter(game_id=game.id)
	
	for message in objs: 
		allMessages += message.message
	if "The describer does not know this city! Please click \"New Game\"!" not in allMessages:
		msg = Message()
		msg.message = "The describer does not know this city! Please click \"New Game\"!"
		msg.handle = 0
		msg.game_role = "GAME"
		msg.game = game 
		notify(game.guesser_id,"The describer does not know this city!")
		msg.save()

	#The next game with an empty describer id needs to be retrieved
	games = Game.objects.filter(describer_id=0, end_time__isnull=True)
	if games:
		game = games[0]

		#Make sure the describer and the guesser cannot be the same player
		if game.guesser_id != request.user.id:
			game.describer_id = request.user.id
			city = City.objects.get(city_id=game.city_id)
			game.last_guess_time = timezone.now()
			game.save()
			notify(game.guesser_id,"Your game has started!")

	#If the current player already is a guesser in an open game 
	#the player needs to be assigned to a new game
	else:
	 	game = storeNewGame(request.user)
	 	city = City.objects.get(city_id=game.city_id)
	 	city.number_played += 1
	 	city.save()
	return render(request, 'game/game.html', {'game': game, 'city':city, 'chat':chat })

def unknown(request, game_id):
	game = Game.objects.get(game_id=game_id)
	return render(request, 'game/unknownCity.html', {'game': game})


def reported_redirect(request, game_id):
	game = Game.objects.get(game_id=game_id)
	reportedUser = CustomUser.objects.get(user_id=request.user.id)
	if reportedUser.reported < 3:
		return render (request, 'game/report.html', {'game':game, 'reported':request.user.id})
	else:
		reported = True
		return render(request, 'game/logout.html', {'game': game, 'reported': reported})

'''
This method manages the game by checking and storing messages submitted to the message board by users. If the city is 
guessed correctly it stores a message to both users informing them about the success. Since spelling variations might not correctly track the correct guess of the city, there is also a button
that allows users to say that the city has already been guessed correcty. 
'''
def playing(request, game_id):
	game = Game.objects.get(game_id=game_id)
	city = City.objects.get(city_id=game.city_id)
	msg = Message()
	msg1 = Message()
	messages = ""
	not_user = ""
	not_message = ""
	variant = ""

	if request.method == "POST":
		message = request.POST['param']
		message = message.translate(str.maketrans({key: None for key in string.punctuation}))
		if message:
			if request.user.id == game.describer_id:	
				msg.game_role = "describer"
				not_user = game.guesser_id
				not_message = "New hint"
			else: 
				msg.game_role = "guesser"
				not_user = game.describer_id
				not_message = "New guess"
			msg.handle = request.user.id
			msg.message = message
			msg.game = game
			game.last_guess_time = timezone.now()
			game.save()
			msg.save()

		info = message.translate(str.maketrans({key: None for key in string.punctuation}))
		info = unidecode(info)
		city_blank = unidecode(city.city_name)
		if "Saint" in city_blank:
			variant = city_blank.replace("Saint", "St")
		if info.lower() == city.city_name.lower() or info.lower() == city_blank.lower() or info.lower() == variant.lower():
			objs = Message.objects.filter(game_id=game.id)
			allMessages = ""

			for message in objs: 
				allMessages += message.message
			if "Congratulations! The city was guessed correctly! Please click \"New Game\"!" not in allMessages:
				msg1 = Message()
				msg1.message = "Congratulations! The city was guessed correctly! Please click \"New Game\"!"
				msg1.handle = 0
				msg1.game_role = "GAME"
				msg1.game = game 
				msg1.save() 

			game.success = True 
			game.end_time = timezone.now()
			game.save()
			not_user = game.describer_id
			not_message = "Congratulations! The city was guessed correctly!"

		objs = Message.objects.filter(game_id=game.id)
		for x in objs:
			messages += x.game_role+ ': '+x.message + ' <br/>'
	notify(not_user,not_message) 
	return HttpResponse({messages})

'''
If a user is reported as abusive by another user, it is communicated to the user and if the user is reported 
more than three times they will be blocked and informed about the blocking
'''
def reported(request, game_id):
	game = Game.objects.get(game_id=game_id)
	objs = Message.objects.filter(game_id=game.id)
	reported = True
	allMessages = ""

	for message in objs: 
		allMessages += message.message
	if "Reported user!" not in allMessages:
		msg = Message()
		msg.message = "Reported user!"
		msg.handle = 0
		msg.game_role = "GAME"
		msg.game = game
		msg.save()

	if request.user.id == game.describer_id:
		reportedUserID = game.guesser_id
	else:
		reportedUserID = game.describer_id

	notify(reportedUserID, "Your message has been reported as abusive.")
	game.end_time = timezone.now()
	game.save()

	reportedAuthUser = User.objects.get(id=reportedUserID)
	reportedUser = CustomUser.objects.get(user_id=reportedUserID)
	mailSubject = "GUESSence: Message reported"
	mailMessage = "Hello "+reportedAuthUser.username+", \n \n"+"""We write to inform you that three of your messages have been reported as abusive by other users and your account has been blocked. Please contact us if you wish to unblock the account at tabooGameEssence@gmail.com.
	\n \nThis measure is taken to ensure the quality of the GUESSence app. Please accept our apologies for any inconvenience caused by this measure.
	\n \nKind regards,
Your developers
your email address"""
	if reportedUser.reported < 3:
		reportedUser.reported += 1
		reportedUser.save()
		return render(request, 'game/report.html', {'game': game, 'reported': reportedUserID})
	else:
		to_list = [reportedAuthUser.email, settings.EMAIL_HOST_USER]
		send_mail(mailSubject, mailMessage,'GUESSence <no-reply@your email address>', to_list, fail_silently=False)
		return render(request, 'game/report.html', {'game': game, 'reported': reportedUserID})

'''
This method gives the describer the option to hit the button "Guess Correct" if the city was guessed 
correctly but due to spelling variation or diacritics the correct guess was not detected
'''
def success(request, game_id):
	msg = Message()
	game = Game.objects.get(game_id=game_id)
	user = User()
	if request.user.id == game.describer_id: 
		user = User.objects.get(id=game.guesser_id)
	else: 
		user = User.objects.get(id=game.describer_id)

	objs = Message.objects.filter(game_id=game.id)
	allMessages = ""

	for message in objs: 
		allMessages += message.message
	if "Congratulations! The city was guessed correctly! Please click \"New Game\"!" not in allMessages:
		msg.message = "Congratulations! The city was guessed correctly! Please click \"New Game\"!"
		msg.handle = 0
		msg.game_role = "GAME"
		msg.game = game 
		msg.save()
	
	game.success = True 
	game.end_time = timezone.now()
	game.save() 
	storeScore(request.user)
	notify(game.guesser_id,"Congratulations! The city was guessed correctly!")
	trackUser = CustomUser.objects.get(user_id=user.id)
	score = trackUser.score
	return render(request, 'game/gameSuccessful.html', {'game': game, 'user': user, 'score': score})

'''
This method consistently queries the database for new messages from either player in 
the game and posts all messages with the same game-id to the message board
'''
@csrf_exempt
def update(request, game_id):
	messages = ""
	game = Game.objects.get(game_id=game_id)
	objs = Message.objects.filter(game_id=game.id)
	for x in objs:
		if x.message == "Congratulations! The city was guessed correctly! Please click \"New Game\"!":
			return HttpResponse({game.game_id})
		if x.message == "The describer does not know this city! Please click \"New Game\"!":
			msg = "x"+str(game.game_id)
			return HttpResponse({msg})
		if x.message == "Reported user!":
			msg = "z"+str(game.game_id)
			return HttpResponse({msg})
		if x.message == "Timeout!":
			msg = "y"+str(game.game_id)
			return HttpResponse({msg})
		else:
			messages += x.game_role+ ': '+x.message + ' <br/>'
	if not messages:
		messages = "No message yet!"
	return HttpResponse({messages})

'''
This method serves to interact with the player in the sense of informing the player
whether another user is online and when a second user has joined the game
'''
@csrf_exempt
def player(request, game_id):
	message = "Wait for 2nd player!"
	game = Game.objects.get(game_id=game_id)
	if game.describer_id == 0 or game.end_time == "Null":
		message = "Wait for 2nd player!"
	else: 
		message = "Game started!"
	return HttpResponse({message})

'''
This method implements a timer to estimate the time between submissions of hints/guesses and display 
the same countdown to both players
'''
@csrf_exempt
def timer(request, game_id):
	game = Game.objects.get(game_id=game_id)
	if game.last_guess_time:
		time = timezone.now() - game.last_guess_time
		if time > timezone.timedelta(seconds=120): 
			time = "None"
		else:
			time = timezone.timedelta(seconds=120) - time
	else:
		time = "None"
	return HttpResponse({time})

def timeout(request, game_id):
	game = Game.objects.get(game_id=game_id)
	game.end_time = timezone.now()
	game.save()
	msgs = ""
	lastGuessUser = 0
	user = User()
	if request.user.id == game.describer_id: 
		user = User.objects.get(id=game.guesser_id)
	else: 
		user = User.objects.get(id=game.describer_id)

	messages = Message.objects.filter(game_id=game.id)
	for message in messages:
		msgs = msgs + message.message
		if message.handle != "0":
			lastGuessUser = message.handle	
			lastGuessUser = int(lastGuessUser)

	if "Timeout!" not in msgs:
		msg = Message() 
		msg.message = "Timeout!"
		msg.handle = 0
		msg.game_role = "GAME"
		msg.game = game
		msg.save()
		notify(game.describer_id,"Your game has timed out!")
		notify(game.guesser_id,"Your game has timed out!")

		if lastGuessUser == game.describer_id:
			trackUser = CustomUser.objects.get(user_id=game.guesser_id)
			trackUser.timeouts = trackUser.timeouts + 0.5
			trackUser.score = trackUser.number_success+(0.1 * (trackUser.number_games-trackUser.number_success))-trackUser.timeouts
			trackUser.save()
		if lastGuessUser == game.guesser_id or lastGuessUser == 0:
			trackUser = CustomUser.objects.get(user_id=game.describer_id)
			trackUser.timeouts = trackUser.timeouts + 0.5
			trackUser.score = trackUser.number_success+(0.1 * (trackUser.number_games-trackUser.number_success))-trackUser.timeouts
			trackUser.save()

	opponent = CustomUser.objects.get(user_id=user.id)
	score = opponent.score
	
	return render(request, 'game/timeout.html', {'game': game, 'user': user, 'score': score})

'''
This method returns the number of active players as stored in "is_active" in the user db 
'''
@csrf_exempt
def playersOnline(request):
	players = User.objects.filter(is_active=True)
	count = 0
	for player in players: 
		count += 1 
	if count == 1: 
		message = 'You are currently the only player.'
	else: 
		message = 'There are '+str(count)+' players online.'
	return HttpResponse({message})

'''
Returns the scores of the top five players and their usernames
'''
@csrf_exempt
def scores(request):
	message = ''
	trackUser = CustomUser.objects.get(user_id=request.user)
	message += "xxx"+str(trackUser.score)+"yyy"
	bestUsers = CustomUser.objects.order_by('-score')[:5]
	for user in bestUsers:
		if user.score > 0:
			user1 = User.objects.get(id=user.user_id)
			message += user1.username+": "+str(user.score)+" "+"<br />"
	return HttpResponse({message})

'''
Utility function to create a random game id 
'''
def getGameId():
	game_id = random.randrange(10000, 100000)
	if not Game.objects.filter(game_id=game_id):
		return game_id 
	else:  
		game_id = random.randrange(10000, 100000)
		return game_id

'''
Utility function to retrieve a city id from the list of cities in the DB 
It filters the city by the number of times the city has been played and 
ensures that the guesser has not already guessed this city
'''
def getCityId(guesser_id):
	city_id = random.randrange(1,227)
	#Build better method for numbers played!
	games = Game.objects.filter(guesser_id=guesser_id)
	guesser_cities = list()
	for game in games: 
		guesser_cities.append(game.city_id)
	played_cities = City.objects.all().order_by('number_played')
	for city in played_cities:
		if city.city_id not in guesser_cities:
			return city.city_id
	return city_id

'''
Utility function to create and store the new game in the DB
'''
def storeNewGame(user):
	game = Game()
	game.guesser_id = user.id
	game.game_id = getGameId()
	game.city_id = getCityId(game.guesser_id)
	game.start_time = timezone.now()
	game.save()
	return game

def storeScore(user):
	trackUser = CustomUser.objects.get(user_id=user.id)
	trackUser.number_success += 1
	trackUser.score = trackUser.number_success+(0.1 * (trackUser.number_games-trackUser.number_success))-trackUser.timeouts
	trackUser.save()

'''
Function to send Firebase messages
'''
def notify(user,message):
	#print(user)
	if(user != 0):
		device_id = DemographicUser.objects.get(user_id=user).deviceID
		if(device_id != '0'):
			payload = {"to" : device_id, "priority": "high","data" : { "body" : message,"title" : "GUESSence"}, "notification" : { "body" : message,"title" : "GUESSence", "sound" : "default", "icon" : "guessence"},"collapse_key" : "GUESSence"}
			headers = {'Authorization' : 'key=your key'}
			url = 'https://fcm.googleapis.com/fcm/send'
			print(requests.post(url,headers=headers,json=payload))
