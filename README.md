# GUESSENCE 

READ ME  

This repository consists of two interlinked applications. The first is a web application that provides the main functionality of this guessing game. The second is an Android mobile application that has been developed to use the functionality of the web application as a backend in the mobile app with added new login functionality. The current version of the mobile app does not function without the web app setup and running on a server.

GUESSence web application 
This web application and mobile app were developed within the context of the ESSENCE project (https://www.essence-network.com/). 

GUESSence is a web application based on the popular board game Taboo (http://www.hasbro.com/common/instruct/Taboo(2000).PDF). It is two-player guessing game where the targets to be guessed are limited to popular cities in the world. There are two roles in the game: a guesser and a describer. The first user to log on to a new game is the guesser. They see a message board, a score board with the best players, and some basic game functionality (log out, new game, help). The second player to log onto a game gest assigned the role of the describer. In addition to the view of the guesser, the describer also sees the target city and a set of taboo words. The city is the one the describer needs to describe to the guesser, the taboo words are words that the describer cannot use to describe the city and against which all inputs of the describer are checked. 

A timer is started when the describer joins the game. They have five minutes to submit the first hint of the city to be described. A hint may only be a noun with an adjectival or verbal modifier no longer than four words and may not contain any named entities. The input is checked and warning messages are issued should the input not comply. The input is also checked for spelling with "did you mean" messages in case of misspelling. Once the hint is submitted the timer restarts and the guesser has five minutes to submit a guess. A guess may only consist of named entities. Once the guesser submits the correct city name the game automatically informs the users and redirects them to a success page where the are informed about the identity of the other player and their score with the option to join a new game. User assignment to games is done automatically on a first come first serve basis. This ensures that players do not chose to play with people they already know and thus submit hints that are based on previous common knowledge.  

The game was designed within the ESSENCE project in order to collect data for an AI challenge. The challenge took place at the IJCAI 2017 (https://www.essence-network.com/challenge/challenge-rules/). In the challenge, the guesser agents were presented with the humanly created hints from the games above and the goal of the agent was to guess a city faster or equally fast to the human guesser. Only games that were successfully completed by human players were included in the challenge to ensure that the hints are of a quality that allow for correctly guessing the city. 

GUESSence mobile application 
The mobile application in the folder GUESSence_mobileApp is an Android app developed in Android Studio that views the web application in an Android frame by means of the webviewer and provides additional login functionality with Facebook, Twitter or email accounts backed by Firebase. The main database backend for the user and message tracking of the mobile app is Firebase, however, the game messages and user information is equally transferred to and stored in the Django backend. 

LICENSE
This software confirms to the Apache 2.0 software license and can be used accordingly.


