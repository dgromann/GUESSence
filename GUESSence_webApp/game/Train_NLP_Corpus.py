# Author: Sarenne Wallbridge 
# Date: July 2016 
# Function: This component takes strings as input and checks them for proper nouns. It issues a warning should the input string 
# 			contain a proper noun. 

import re
import collections
import nltk
import nltk.corpus
from nltk.corpus import wordnet as wn
from nltk.corpus import brown
from nltk.corpus import reuters
from nltk.corpus import gazetteers
import cPickle
import string
import math
import itertools
#import MySQLdb
#import MySQLdb.cursors
import nltk.data
import pandas

from Truecaser import *
from TrainFunctions import *
from EvalTruecaser import *
from SpellChecker import spellCheck


'''
Trains the Truecaser using functions from TrainFunctions.py and stores information in 'distributions___.obj'.  Training can be done using 
sets of sentences (sent()) from a corpus or set of corpora from nltk, or using a properly-cased text file containing a sentence on each line. 
Currently, this is being done using a text file containing 100'000 sentences from random Wikipedia articles.
@input: None (name of target .obj file)
@output: None (updates target .obj file)
'''
def trainTC(): 
	uniDist = nltk.FreqDist()
	backwardBiDist = nltk.FreqDist() 
	forwardBiDist = nltk.FreqDist() 
	trigramDist = nltk.FreqDist() 
	wordCasingLookup = {}

	# :: Option 1: Train it based on NLTK corpus ::
	# Uncomment, if you want to train from set of corpora
	"""print "Update 'NPL' from NLTK WordNet Corpus"
	NLTKCorpus = wn.words()
	# NLTKCorpus = brown.sents()+reuters.sents()+nltk.corpus.semcor.sents()+nltk.corpus.conll2000.sents()+nltk.corpus.state_union.sents()
	## NLTKCorpus is the corpus used to train the Truecaser
	updateDistributionsFromSentences(NLTKCorpus, wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)
	"""

	# :: Option 2: Train it based the train.txt file ::
	# Uncomment, if you want to train from train.txt
	print "Update from train.txt file"
	sentences = []
	for line in open('one_meelyun_sentences.txt'):        
	    sentences.append(line.decode('utf-8').strip())
	    
	tokens = [nltk.word_tokenize(sentence) for sentence in sentences]
	updateDistributionsFromSentences(tokens, wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)	  

	f = open('distributionsWiki.obj', 'wb')
	cPickle.dump(uniDist, f, protocol=cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(backwardBiDist, f, protocol=cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(forwardBiDist, f, protocol=cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(trigramDist, f, protocol=cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(wordCasingLookup, f, protocol=cPickle.HIGHEST_PROTOCOL)
	f.close()


'''
Takes the raw hint as input.  Input is seperated into segements determined by punctuation to ensure a good tagging accuracy 
and each segment is processed individually.  Each word is spell-checked and can be replaced with the most-likely correct word if the user 
chooses.  The hint is also formated to be fed into the truecaser (everything is lower cased and a period is added to the end of each segement)
@input: String 
@output: List
'''
# def extractInfo(input): # Formats input (hint) to be fed into the Truecaser after performing a spellCheck. 
	
# 	lowerInput = input.lower()
# 	if lowerInput.startswith("the") or lowerInput.startswith("a ") or lowerInput.startswith("no") or lowerInput.startswith("yes"):
# 		info = ""
# 	else:
# 		info = "the"

# 	raw = nltk.word_tokenize(input.lower())
# 	for i in range(0, len(raw)):
# 		word = raw[i]
# 		if (word == 'the') and not(info.endswith('the ')):
# 			info = info + ' ' + word 
# 		if re.match('^[\w]+$', word): # Maybe add '-' here to deal with hyphenated words
# 			newWord = spellCheck(word)
# 			info = info + ' ' + newWord
# 		if re.match('[.,!-]', word) and not(re.match('[.,!-]', raw[i -1])): # removes multiple punctuation marks
# 			info = info + '.\nthe'

# 	if info.endswith("the"):
# 		info = info[:-4]
# 	if not info.endswith("."):
# 		info = info + "."

# 	info = info.split('\n')
# 	return info


def extractInfo(input):
	output = []
	info = re.split('[.,!?]*', input.lower())  	# list of phrases (strings) seperated at punctuation marks
	info = filter(None, info) 			# ensure there is no empty strings in list
	for rawPhrase in info:
		phrase = ''
		rawWords = nltk.word_tokenize(rawPhrase)
		
		# check spelling
		for rawWord in rawWords:
			if not(re.match('[a-zA-Z0-9]', rawWord)):   # check for 'words' of just punctutation (eg ':)')
				phrase = phrase
			else:
				# what to do with apostrophes
				word = spellCheck(rawWord)
				phrase = phrase + word + ' '
		
		# add formatting for tagging
		if len(phrase) > 0:
			words = nltk.word_tokenize(phrase)
			tags = nltk.pos_tag(words)
			firstTag = tags[0][1] 
			print "first word: (" + words[0] + "," + firstTag + ")"
			theTags = ['JJ','NN','NNS','NNP','NNPS']
			wordList = ['ok', 'hello', 'hi', 'no', 'nope', 'yes', 'oui', 'oh']
			if (firstTag in theTags):
				if (len(words) == 1 and (firstTag == 'JJ' or firstTag == 'JJR')):
					phrase = 'a ' + phrase + 'object'
				elif not(words[0] in wordList):
					phrase = 'a ' + phrase
			phrase = phrase + '.' 
			output.append(phrase)
	return output


'''
Checks if a word is a nationality or language by checking if each natWord (country, language, adjective) occurs in 'information'.  It acts as a 
coarse filter before hints are truecased and tagged.  I may add directions and their descriptors to Nationalities.txt.
@input: list (hint seperated into phrases by exractInfo())
@output: word (if any) from hint contained in Nationalities.txt
'''
def natCheck(information):
	infoStr = ' '.join(information)
	natList = open('Nationalities.txt').read().lower()
	for line in natList.split('\n'):
		for natWord in line.split('.'):
			if not(natWord == '') and natWord in infoStr:
				return natWord.title()
	return None


'''
Checks if hint contains a direction (N,S,E,W) or and adjective describing a direction (e.g. southern)
@input: list (hint seperated into phrases by extractInfo())
@output: word (if any) from hint contained in Directions.txt
'''
def dirCheck(information):
	infoStr = ' '.join(information)
	dirList = open('Directions.txt').read().lower()
	for dirWord in dirList.split('.\n'):
		if not(dirWord == '') and (dirWord in infoStr):
			return dirWord.title() 
	return None


'''
Checks the number of phrases contained in a hint. 'n' parameter represents the number of phrases accepted by the function - hints may be 
allowed more phrases (2, eg. 'no. straight streets') than a guess which should only be one (i.e. a city)
@input: list of input phrases
@output: boolean value(False if number of phrases (count) exceeds n) 
'''
def inputLengthCheck(inputList, n):
	count = len(inputList)
	print "number of phrases: ", count
	if count > n:
		return False
	return True 


'''
Checks the number of words in a phrase and returns True or False corresponding to whether there are fewer than n words in a phrase. 'n' 
parameter represents the number of words accepted by the function.  
@input: list of input phrases
@output: boolean value (False if number of words (wordCount) exceeds n)
'''
def phraseLengthCheck(phrase, n):
	wordCount = len(nltk.word_tokenize(phrase)) - 1 # periods are counted as words so substract 1 from count
	print "word count [", phrase,"]: ", wordCount
	if wordCount > n:
		print "too long"
		return False 
	return True

'''
Checks if a phrase contains the basic content required to make up an appropriate hint/guess.  Perhaps change the tagset depending on the role 
of the unser (tagsetD = tags required for a hint, tagsetG = tags required for a guess)
@input: list of input phrases
@output: boolean value (False if hint does not contain nessessary content)
'''
def phraseContentCheck(phrase, role):
	taggedWordList = nltk.pos_tag(nltk.word_tokenize(phrase))
	tagList = [x[1] for x in taggedWordList]
	if (role == "d"):
		tagSet = ["JJ", "NN", "NNS", "NNP", "NNPS", "VB"]
	else:
		tagSet = ["NN", "NNS", "NNP", "NNPS"]
	contains = [i for i in tagSet if i in tagList]
	if (contains == []):
		return False
	return True


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
def describerCheck(input): #Replace information with input when done testing
	f = open('distributionsWiki.obj', 'rb')
   	uniDist = cPickle.load(f)
   	backwardBiDist = cPickle.load(f)
   	forwardBiDist = cPickle.load(f)
   	trigramDist = cPickle.load(f)
   	wordCasingLookup = cPickle.load(f)
   	
   	# format and spellCheck hint using extractInfo to be fed into the trueCaser
	print "..... raw input ..... " + "\n" + input
	information = extractInfo(input)	
	print "..... hint information ....."
	print information  # information is a list of phrases

	# Check if hint contains too many phrases and produce a WARNING message
	if not(inputLengthCheck(information, 3)):
		return "WARNING! You have submitted too many phrases.\n-------------------\n"

	# For each phrase, ensure it is not too long (too many words) and that it contains an appropriate content, else produce a WARNING message
	for phrase in information:
		if not(phraseLengthCheck(phrase, 4)):
			return "WARNING! You have submitted a phrase that is too long. Hints should be less than 4 words.\n-------------------\n"
		if not(phraseContentCheck(phrase, 'd')):
			return "WARNING! You have submitted an inappropriate hint.  Hints should contain nouns, adjectives, verbs, or a combination of these.\n-------------------\n"

	# Check if a word from Nationalities.txt is contained in the hint (information) and produce a WARNING message
	if not(natCheck(information) == None):
		return "WARNING! '" + natCheck(information) + "' is a nationality or language and should not be used as a hint.\n-------------------\n"

	# Check if a word from Directions.txt is contained in the hint (information) and produce a WARNING message
	if not(dirCheck(information) == None):
		return "WARNING! '" + dirCheck(information) + "' is a direction and should not be used as a hint.\n-------------------\n"

	# For each phrase, truecase the phrase and tag each cased word to check for NNP.  Produce a WARNING message if hint contains an NNP
	for phrase in information:
		print "..... corrected tags ....."  
		tokensTrueCase = evaluateTrueCaser([phrase], wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)
		taglist = nltk.pos_tag(tokensTrueCase)
		print taglist
		for (word, tag) in taglist:
			if (tag == "NNP") or (tag == "NNPS"):
				return "WARNING! '" + word + "' may be a proper noun and should not be used as a hint."
		print "-------------------\n"
	
	f.close()


'''
Checks the input of a guesser to ensure that it does not contain too many phrases or any phrases that are too long.  It also ensures that the 
guess contains the appropriate content using a very coarse filter(ie.the guess must contain an NN or NNP).
@input: String (guess)
@output: Warning (if any)
'''
def guesserCheck(input):
	information = extractInfo(input) # List of phrases. Should be one phrase consisting of a city name.

	# Check if hint contains too many phrases and produce a WARNING message
	if not(inputLengthCheck(information, 2)):
		return "WARNING! You have submitted too many phrases"

	# For each phrase, ensure it is not too long (too many words) and that it contains an appropriate content, else produce a WARNING message
	for phrase in information:
		if not(phraseLengthCheck(phrase, 4)):
			return "WARNING! You have submitted a phrase that is too long. Guesses should be less than 4 words"
		if not(phraseContentCheck(phrase, 'g')):
			return "WARNING! You have submitted an inappropriate guess.  Guesses should contain only city names"
	print "-------------------\n"


'''
This function simulates a game between two players (a describer and guesser) where each players input is proceded by their role tag 
('describer> ...' or 'guesser> ...') and both players must take turns to submit input to the game chat.  TabooGame() uses an inifite for-loop 
to keep track of the current turn (d/g). For each turn, the component prompts the corresponding player for input. The input role tags are used 
to ensure that only the correct player can submit input.  If the turn and role of the player match, their input is run through the corresponding 
input check - if warnings are thrown, the player is asked to resubmit a hint.  A turn only ends when the right player submits and appropriate 
hint. 
@input: None - input from command line is used when function is running
@output: None - warning messages may be thrown
'''
def tabooGame():

	for turn in itertools.cycle(['d', 'g']): # could be replaced by a list of n pairs of 'd' and 'g' to ensure that 
		print "Turn: ",turn
		if (turn == 'd'):
			rawInput  = raw_input("Describer, please submit a hint: ")
		elif (turn == 'g'):
			rawInput = raw_input("Guesser, please guess a city: ")
		
		# Ensure that the correct player is submitting input (turn taking)
		role = rawInput[0] 
		print "Role: ",role
		while not(role == turn):
			rawInput = raw_input("Please wait for your turn... ")
			role = rawInput[0]

		# Check the describer's hint using describerCheck()
		if (turn == 'd'):
			print "1\n"
			# rawHint = rawInput[11:]
			hintWarning = describerCheck(rawInput[11:])
			while not(describerCheck(rawInput[11:]) == None):
				hintWarning = describerCheck(rawInput[11:])
				print hintWarning # why is this calculation being done twice?? (same in guesser loop)
				rawInput = raw_input("Please submit another hint: ")
				role = rawInput[0] 
				while not(role == turn): # still ensure correct player is submitting input
					rawInput = raw_input("Please wait for your turn... ")
					role = rawInput[0]

		# Check the guesser's guess using guesserCheck()
		elif (turn == 'g'):
			# rawGuess = rawInput[9:]
			guessWarning = guesserCheck(rawInput[9:])
			while not(guesserCheck(rawInput[9:]) == None):
				guessWarning = guesserCheck(rawInput[9:])
				print guesserWarning
				rawInput = raw_input("Please submit another guess: ")[9:]
				role = rawInput[0] 
				while not(role == turn): # still ensure correct player is submitting input
					rawInput = raw_input("Please wait for your turn... ")
					role = rawInput[0] 


tabooGame()

def readInput():
	#get the data
	df = pandas.read_csv('Taboo_AllGames.csv')
	mtaboos = df.tabooWords
	df = df[df.role == 'describer']
	messages = df.message
	return messages

# if __name__ == "__main__":       
   	
# trainTC()  This is commented out because the truecaser has already been trained.  Uncomment this line to retrain the truecaser.

# inf = "salty water." 
# inf2  = "Paris"
# print phraseLengthCheck("try again .", 5)
# print describerCheck(inf)
# print (describerCheck(inf) == None)
# print guesserCheck(inf2)


'''
This function runs the guesser on the game dataset.
'''
# def main():
# 	hints = set()
# 	hints = readInput()
# 	for word in hints:
# 		print "Word: " + word 
# 		extractCase(word)
# 	#extractCase('Beatles')

# if __name__ == "__main__":
#     main()
