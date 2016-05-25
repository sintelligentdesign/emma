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
import cfg                          # Misc.

def main():
    ### every loop, Emma decides what she wants to do.
    # todo: add choice cooldown
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
        
        ## generate associations from the sentence
        inputPOSList = nltk.pos_tag(inputAsWords)                       # get the parts of speech for our sentence
        conceptgen.findassociations(inputAsWords, inputPOSList)         # look for associations and sent them to Emma's Concept Graph
        
        ## find nouns in our input and add them to a noun list to help Emma choose what words to use when she responds
        # todo: check for and remove duplicates
        nounList = []
        nounCodes = cfg.nounCodes()
        inputAsPOS = []                                                 # define inputAsPOS
        for count in range(0, len(inputPOSList)):
            inputPOSTuple = inputPOSList[count]
            inputAsPOS.append(inputPOSTuple[1])

        for count in range(0, len(inputAsWords)):                       # create nounList
            if inputAsPOS[count] in nounCodes:
                nounList.append(inputAsWords[count])
        
    ### now Emma generates a response
    # todo: have this loop n number of times to create multiple sentences
    ## generate a new sentence template from our template model
    replyTemplate = sentencetemplategen.generate()
            
    ## check for existing associations with nouns in our list
    # todo: check for and remove duplicates
    relatedNouns = []
    relatedVerbs = []
    relatedAdjectives = []
    
    for count in range(0, len(nounList)):
        relatedNouns.append(broca.findrelatedwords(nounList[count], 0))
        relatedVerbs.append(broca.findrelatedwords(nounList[count], 1))
        relatedAdjectives.append(broca.findrelatedwords(nounList[count], 2))
        
    print "Related nouns: " + str(relatedNouns)
    print "Related verbs: " + str(relatedVerbs)
    print "Related adjectives: " + str(relatedAdjectives)

while 1 > 0:
    main()