# -*- coding: utf-8 -*-

#   .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
#  d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
#  888ooo888  888   888   888   888   888   888   .oP"888
#  888    .,  888   888   888   888   888   888  d8(  888
#  `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o
#
#  ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
#
#          EXPANDING MODEL of MAPPED ASSOCIATIONS
#
#
#     Written by Ellie Cochran & Alexander Howard, with
#                contributions by Omri Barak.
#
#      Uses elements from the Natural Language Toolkit.
#                 Visit http://www.nltk.org.

import nltk                         # Natural Language Toolkit
import conceptgen, posmodelgen      # Learning packages
import sentencetemplategen, broca   # Reply packages

### Load list of banned words into a dictionary so that we can remove them later
bannedWordsFile = open('emma.brn/bannedwords.txt', 'r') # todo: make .brn file choosable
bannedWords = []
for line in bannedWordsFile:                            # pump banned words into a list, word by word
    bannedWord = bannedWordsFile[line].rstrip('\n')     # remove newline characters as we add banned words to the list
    bannedWords.append(bannedWord)
bannedWordsFile.close()

### Define what parts of speech signify nouns, verbs, and adjectives
nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adjectiveCodes = ['JJ', 'JJR', 'JJS']
    
def main():
    ### every loop, Emma decides what she wants to do.
    # todo: add logic to decisions: try to keep new word list smallish, have a timer limit sleeping, default to "usually" answering questions
    decision = 0
    if decision == 0:       # Answer Tumblr questions
        conversate()
    elif decision == 1:     # Study new words
        pass    # todo: link this up
    elif decision == 2:     # Sleep for 15 or so loops
        pass    # todo: link this up

def conversate():
    ### Emma reads input, learns from it, and generates a response
    # todo: link this with ask reader in tumblrclient.py
    # todo: add commandline-based communication as a commandline flag when starting
    inputAsParagraph = raw_input('You >> ')                     # todo: link this to tumblr, maybe have choice of input and output part of main()
    inputAsSentences = nltk.sent_tokenize(inputAsParagraph)     # segment the paragraph into a list of sentences
    inputAsWords = []                                           # segment each sentence into a list of words
    
    for sentence in range(0, len(inputAsSentences)):
        ### for each sentence, run learning functions
        inputAsWords = nltk.word_tokenize(inputAsSentences[sentence])   # tokenize words in each sentence
        
        posmodelgen.grok(inputAsWords)                                  # learn sentence structure from the sentence's parts of speech pattern
        
        ## remove banned words before we form association, since we don't want to form any associations for those.
        # todo: move banned word file > list outside of for loop
        bannedWordsFile = open('emma.brn/bannedwords.txt', 'r')         # todo: make .brn file choosable
        bannedWords = []
        for line in bannedWordsFile:                                    # pump banned words into a list, word by word
            bannedWord = bannedWordsFile[line].rstrip('\n')             # remove newline characters as we add banned words to the list
            bannedWords.append(bannedWord)
        bannedWordsFile.close()
        # now that the list of banned words is ready, remove any bad words
        wordsToRemove = []
        for word in inputAsWords:
            if word.lower() in bannedWords:
                wordsToRemove.append(word)
        wordsToRemove.reverse()
        for word in wordsToRemove:
            inputAsWords.remove(word)
            #print 'removing bad word "%s"' % word
        
        # get the parts of speech for our sentence and unzip it so that we can get the parts of speech (we already have a word list)
        inputPOSList = nltk.pos_tag(input)
        
        # look for associations to send to Emma's Concept Graph
        conceptgen.findassociations(inputPOSList)

while 1 > 0:
    main()