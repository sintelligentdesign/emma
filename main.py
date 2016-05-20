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
    
    # Generate sentence model from input sentences
    posmodelgen.grok(inputAsWords)