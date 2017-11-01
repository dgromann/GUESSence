# -*- coding: utf8 -*-
#
# Author: Dagmar Gromann <dagmar.gromann@gmail.com>, Sarenne Wallbridge
#
# Support function of the NLP and spellchecker of the main application
# Function: Evaluate the TrueCaser implemented in this web application

from game.Truecaser import *
import pickle
import nltk
import string

'''
Main class to evaluate the functioning of the implemented TrueCaser to obtain the optimal casing for 
a given input string
'''
def evaluateTrueCaser(testSentences, wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist):
    correctTokens = 0
    totalTokens = 0
    
    for sentence in testSentences:
        tokensCorrect = nltk.word_tokenize(sentence)
        tokens = [token.lower() for token in tokensCorrect]
        tokensTrueCase = getTrueCase(tokens, 'title', wordCasingLookup, uniDist, backwardBiDist, forwardBiDist, trigramDist)

        perfectMatch = True
        
        for idx in range(len(tokensCorrect)):
            totalTokens += 1
            if tokensCorrect[idx] == tokensTrueCase[idx]:
                correctTokens += 1
            else:
                perfectMatch = False
        
      
    return tokensTrueCase
