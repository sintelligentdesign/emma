# -*- coding: utf-8 -*-

#   .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.   
#  d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b  
#  888ooo888  888   888   888   888   888   888   .oP"888  
#  888    .o  888   888   888   888   888   888  d8(  888  
#  `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o
# 
#  ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
#  
#              ENGLISH MODEL of MAPPED ARRAYS
#  
#  
#     Written by Ellie Cochran & Alexander Howard, with
#                contributions by Omri Barak.
#
#      Uses elements from the Natural Language Toolkit.
#                 Visit http://www.nltk.org.

import nltk, conceptgen, posmodelgen

inputAsParagraph = "Hello friend. The quick brown fox jumped over the lazy dog."


inputAsSentences = nltk.sent_tokenize(inputAsParagraph)     # NLTK default sentence segmenter

for count in (0, len(inputAsSentences) - 1):
    inputAsWords = inputAsSentences[count]
    inputAsWords = nltk.word_tokenize(inputAsWords)         # NTLK default word tokenizer
    print "Input sentence is: %s" % inputAsWords
    
    posmodelgen.grok(inputAsWords)                          # Generate sentence model from input sentences
    
    # Generate concept using words in input sentences
    nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
    verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adjectiveCodes = ['JJ', 'JJR', 'JJS']
    inputAsPartsOfSpeech = posmodelgen.getPartsOfSpeech(inputAsWords)
    
    # check if the word is one we care about (a noun, verb, or adjective)
    for count in range(0, len(inputAsPartsOfSpeech)):
        # check if word is a noun
        for code in range(0, len(nounCodes)):
            if inputAsPartsOfSpeech[count] == nounCodes[code]:
                print "word %s is a noun!" % inputAsWords[count]
        for code in range(0, len(verbCodes)):
            if inputAsPartsOfSpeech[count] == verbCodes[code]:
                print "word %s is a verb!" % inputAsWords[count]
        for code in range(0, len(adjectiveCodes)):
            if inputAsPartsOfSpeech[count] == adjectiveCodes[code]:
                print "word %s is an adjective!" % inputAsWords[count]
        