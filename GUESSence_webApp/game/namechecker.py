# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>, Sarenne Wallbridge
#
# Support function of the NLP and spellchecker of the main application
# Function: Main controller of input restrictions - different methods for different game roles (guesser, describer)

import pandas as pd
import pickle
import nltk
import re
import string
from game import spellchecker as spell
import csv


from nltk.tag import StanfordNERTagger
from game.Truecaser import *
from game.EvalTruecaser import *
from nltk.tag.perceptron import PerceptronTagger
tagger = PerceptronTagger()

st = StanfordNERTagger("/var/www/html/cgi-bin/game/stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz", "/var/www/html/cgi-bin/game/stanford-ner/stanford-ner.jar")

cities = list()
file = open('game/data/worldcitiespop.txt', 'r', encoding="utf8")
reader = csv.reader(file)
for row in reader: 
	cities.append(row[1])
	cities.append(row[2]) 
cities.append("Rome")
cities.append("rome")
	

f = open('game/data/distributionsWiki.obj', 'rb')
uniDist = pickle.load(f)
backwardBiDist = pickle.load(f)
forwardBiDist = pickle.load(f)
trigramDist = pickle.load(f)
wordCasingLookup = pickle.load(f)

'''
Checks if a word is a nationality or language by checking if each natWord (country, language, adjective) occurs in 'information'.  It acts as a 
coarse filter before hints are truecased and tagged.  I may add directions and their descriptors to Nationalities.txt.
@input: list (hint seperated into phrases by exractInfo())
@output: word (if any) from hint contained in Nationalities.txt
'''
def natCheck(phrase):
	inf = phrase.lower()
	natList = pickle.load(open("game/data/nationalities.pkl", "rb"))
	if inf in natList: 
		return True
	return False

'''
Checks if hint contains a direction (N,S,E,W) or and adjective describing a direction (e.g. southern)
@input: list (hint seperated into phrases by extractInfo())
@output: word (if any) from hint contained in Directions.txt
'''
def dirCheck(phrase):
	inf = phrase.lower()
	dirs = ["north", "south", "east", "west"]
	for element in dirs: 
		if element in inf: 
			return element
	return None

'''
Checks if a phrase contains the basic content required to make up an appropriate hint/guess.  Perhaps change the tagset depending on the role 
of the unser (tagsetD = tags required for a hint, tagsetG = tags required for a guess)
@input: list of input phrases
@output: boolean value (False if hint does not contain nessessary content)
'''
def phraseContentCheck(phrase, role):
	tags = tagger.tag(nltk.word_tokenize(phrase))
	tagList = [x[1] for x in tags]
	
	if (role == "d"):
		tagSet = ["JJ", "NN", "NNS", "NNP", "NNPS", "VB", "VBG"]
	else:
		tagSet = ["NN", "NNS", "NNP", "NNPS"]
	contains = [i for i in tagSet if i in tagList]
	if (contains == []):
		return False
	return True

def nameChecker(phrase):	
	tags = tagger.tag(nltk.word_tokenize(phrase))
	sent =  nltk.ne_chunk(tags, binary=True)
	for element in sent:
		if hasattr(element, 'label'):
			if element.label() == "NE":
				return element
	return None

'''
Guesser input restrictions are only city names which are checked by this method 
and a warning message is returned if the input does not comply
'''
def guesserCheck(phrase):
	info = phrase.translate(str.maketrans({key: None for key in string.punctuation}))
	if "st" in info.lower():
		info = info.lower().replace("st", "saint")
	hasdigit = any(char.isdigit() for char in info)
	if hasdigit:
		return "Please do not use numbers!"

	if len(info) > 0:
		if info in cities or info == "no clue":
			return None
		else: 
			tokensTrueCase = evaluateTrueCaser([info], wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)
			if st.tag(tokensTrueCase)[0][1] == "LOCATION":
				return None
			else: 
				return "WARNING: Are you sure your guess is a city name or \"no clue\"?"
	else: 
		return "Please do not use punctuation or leave your input empty!"

'''
This function checks dscribers hints. It takes the raw hints as imput and returns a warning message if the hint is not appropriate. It calls 
extractInfo() to spellCheck and format the hint in to a list of phrases to be truecased.  The length of the list of phrases and of each phrase 
is then checked.  Before being truecased, each hint segment (phrase) is run through the natChecker to check for countries, nationalities or 
languages, and dirCheck to ensure the hint does not contain directions.  If it does, describerCheck() throws a warning message and finishes.  If
not, input segments are sequentially cased and tagged.  If a word is tagged as a NNP or NNPS, a warning is flagged.  

A lot of print statements have been left in in to evaluate the performance of the code, however the final version will simply return warnings 
for spelling mistakes, length, nationalities, directions or names entities.
@input: String (hint) and information from TrueCaser
@output: warnings (if any)
'''	
def describerCheck(phrase, tabooWords):	
 
	#Remove punctuation
	info = phrase.translate(str.maketrans({key: None for key in string.punctuation}))
	info = info.strip()	
	info = re.sub(' +',' ',info)
	infoList = info.split(" ")	

	if len(info) == 0: 
		return "Please do not use punctuation or leave your input empty."

	hasdigit = any(char.isdigit() for char in info)
	if hasdigit:
		return "Please do not use numbers!"

	#Check length of max 4 words
	if len(infoList) > 4: 
		return "Length: use noun phrases of max. 4 words - please retype your hint!"

	#Check spelling for each input word and checks for nationalities	
	for word in infoList:
		lowerCWord = word.lower()
		if lowerCWord == "and" or lowerCWord == "or":
			return "Please do not use conjunctions such as \"and\" or \"or\"."
		if lowerCWord in tabooWords: 
			return "\""+word+"\" is a Taboo word! Do not use the words listed below the city name!"
		cWord = spell.spellCheck(word)
		if not cWord == word:
			output = info.replace(word, cWord)
			return "Spelling: Did you mean "+output+ " instead of "+info+"?"
		if natCheck(word):
			return "WARNING: "+word+" looks like a name. If you don't think it's a name, choose \"Submit as is\" to enter it, \"Modify\" to modify the hint."
			#return "WARNING: Please do not use names such as "+ word +". Do you want to submit it because it is not a name?"

	name = nameChecker(info)
	if not(name == None):
		return "WARNING: "+info+" looks like a name. If you don't think it's a name, choose \"Submit as is\" to enter it, \"Modify\" to modify the hint."
		#return "WARNING: Name - please do not use names such as "+ info +". Do you want to submit it because it is not a name?"

	# Checks if input contains cardinal direction
	if not(dirCheck(info) == None):
		return "Cardinal direction: Your hint contains "+dirCheck(info)+" which looks like a direction. Please use a hint without directions."

	#For each phrase, truecase the phrase and tag each cased word to check for NNP.  Produce a WARNING message if hint contains an NNP
	tokensTrueCase = evaluateTrueCaser([info], wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)
	taglist = nltk.pos_tag(tokensTrueCase)

	for (word, tag) in taglist:
	 	if (tag == "NNP") or (tag == "NNPS"):
	 		return "WARNING: "+info+" looks like a name. If you don't think it's a name, choose \"Submit as is\" to enter it, \"Modify\" to modify the hint."
	return None
