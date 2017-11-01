# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>, Sarenne Wallbridge
#
# Support function of the NLP and spellchecker of the main application
# Function: SpellChecker contains the functions nessesary to perform spell check and recommendations
#           to users in the sense of "did you mean...?"


import re
import collections
import nltk
import sys 
from nltk.corpus import wordnet as wn


'''
Takes a raw hint as input and iterates over each word in the input.  If the word is not 
in the corpus (currently using the Brown corpus but am experimenting with different corpora), the 
user is notified and asked if they would like to submit the original word or use the spell checker - I
am considering changing this;
'''
def spellCheck(word):
    if not inWordNet(word):
        return correct(word)
    else:
        return word

'''
Function returns a list of words where words are sequences of lower case alphabetic characters
'''
def words(text):
    return re.findall('[a-z]+', text.lower())

'''
Function trains a probability model - counts occurances of each word
'''
def train(features): 
    model = collections.defaultdict(lambda: 1) ## hashtable with default value of 1 (smoothing in case a word is novel)
    for f in features:
        model[f] += 1
    return model

def addWord(word):
    if word not in NWORDS:
        NWORDS[word] = 1
        print("added for first time", word)
    else:
        NWORDS[word] +=1
        print("added again", word)

def edits1(word):
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts    = [a + c + b     for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in NWORDS)

def known(words):
    return set(w for w in words if w in NWORDS)

def query_1_2_3(word):
    prompt = " [1/2/3] "
    question = "'"+ word + "' " + "is not recognised.  Do you want to use it?  Choose: \n'1' to use '" + word + "', \n'2' to use '" + correct(word) + "' or \n'3' to retype the word"
    one = set(['1'])
    two = set(['2'])
    three = set(['3'])

    sys.stdout.write(question + '\n' + prompt)
    choice = input().lower()
    if choice in one:
        addWord(word)
        return word
        # tag word to be checked for spelling later
    elif choice in two:
        return correct(word)
    elif choice in three:
        newWord = input("Please retype your word: ")
        return newWord
    else:
        sys.stdout.write("Please respond with '1', '2' or '3'")


def inWordNet(word):
    basicWords = ['the', 'and', 'of']
    if not(wn.synsets(word) == []) or (word in basicWords) or word in NWORDS:
        return True 
    return False

def correct(word):
    candidates = known([word]) or known(edits1(word)) or    known_edits2(word) or [word]
    return max(candidates, key=NWORDS.get)


NLPCorpus = wn.words()
NWORDS = train(NLPCorpus)
alphabet = 'abcdefghijklmnopqrstuvwxyz'
