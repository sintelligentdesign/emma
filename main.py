# -*- coding: utf-8 -*-

#   .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
#  d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
#  888ooo888  888   888   888   888   888   888   .oP"888
#  888    .o  888   888   888   888   888   888  d8(  888
#  `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o
#
#  ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
#
#           ENGLISH MODEL of MAPPED ASSOCIATIONS
#
#
#     Written by Ellie Cochran & Alexander Howard, with
#                contributions by Omri Barak.
#
#      Uses elements from the Natural Language Toolkit.
#                 Visit http://www.nltk.org.

import nltk, conceptgen, posmodelgen

inputAsParagraph = "Hello world. The quick brown fox jumped over the lazy dog."


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

    conceptreader(inputAsWords, inputAsPartsOfSpeech)


#find associations of nouns to other words
def conceptreader(inputAsWords, inputAsPartsOfSpeech):
    noun = ""
    associationType = 0
    association = ""
    proximity = 0

    for count1 in range(0, len(inputAsWords)):                                  # finds a noun

        if inputAsPartsOfSpeech[count1] in nounCodes:
            noun = inputAsWords[count1]

            for count2 in range(count1 + 1, len(inputAsWords)):                 # looks for word after
                importantWord = True
                if inputAsPartsOfSpeech[count2] in nounCodes:
                    associationType = 0
                elif inputAsPartsOfSpeech[count2] in verbCodes:
                    associationType = 1
                elif inputAsPartsOfSpeech[count2] in adjectiveCodes:
                    associationType = 2
                else:
                    importantword = False

                if importantWord:
                    association = inputAsWords[count2]
                    proximity = count2 - count1
                    print noun + " " + str(associationType) + " " + association + " " + str(proximity)

            for count3 in range(0, count1):                                     # looks for word before
                importantWord = True
                if inputAsPartsOfSpeech[count3] in nounCodes:
                    associationType = 0
                elif inputAsPartsOfSpeech[count3] in verbCodes:
                    associationType = 1
                elif inputAsPartsOfSpeech[count3] in adjectiveCodes:
                    associationType = 2
                else:
                    importantWord = False

                if importantWord:
                    association = inputAsWords[count3]
                    proximity = count1 - count3
                    print noun + " " + str(associationType) + " " + association + " " + str(proximity)
                    conceptgen.addconcept(noun, associationType, association, proximity)