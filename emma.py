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

import utilities, nltk, conceptgen, posmodelgen

inputAsParagraph = raw_input('You >> ')                     # since we're going to be responding to Tumblr asks, we'll assume that all input will be paragraph form.
                                                            # todo: add alternative ways to input

bannedWordsTxt = open("emma.brn/bannedwords.txt", "r")               # load naughty words into a list so that we can screen for them
bannedWords = []
for line in bannedWordsTxt:
    bannedWords.append(line)
bannedWordsTxt.close()
for count in range(0, len(bannedWords)):
    bannedWords[count] = bannedWords[count].rstrip('\n')

inputAsSentences = nltk.sent_tokenize(inputAsParagraph)     # NLTK default sentence segmenter
inputAsWords = []
for sentence in range(0, len(inputAsSentences)):
    # tokenize input sentence
    inputAsWords.append(inputAsSentences[sentence])
    inputAsWords = nltk.word_tokenize(inputAsSentences[sentence])           # NTLK default word tokenizer
    posmodelgen.grok(inputAsWords)                                          # generate sentence model from input sentences

    # generate concept using words in input sentences
    nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
    verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    adjectiveCodes = ['JJ', 'JJR', 'JJS']
    inputAsPartsOfSpeech = posmodelgen.getPartsOfSpeech(inputAsWords)

    # remove banned words from inputAsWords
    wordstoremove = []
    for word in inputAsWords:
        if word.lower() in bannedWords:
            wordstoremove.append(word)
    wordstoremove.reverse()
    for word in wordstoremove:
        inputAsWords.remove(word)
        print "removing naughty word \"%s\"" % word

# find associations of nouns to other words
def conceptreader(inputAsWords, inputAsPartsOfSpeech):
    noun = ""
    associationType = 0
    association = ""
    proximity = 0

    for count1 in range(0, len(inputAsWords)):                                      # finds a noun
        if inputAsPartsOfSpeech[count1] in nounCodes:
            if inputAsPartsOfSpeech[count1] not in bannedWords:
                noun = inputAsWords[count1]

                for count2 in range(count1 + 1, len(inputAsWords)):                 # looks for important word after noun   todo: turn this and the next code block into a function
                    importantWord = True
                    if inputAsPartsOfSpeech[count2] in nounCodes:
                        associationType = 0
                    elif inputAsPartsOfSpeech[count2] in verbCodes:
                        associationType = 1
                    elif inputAsPartsOfSpeech[count2] in adjectiveCodes:
                        associationType = 2
                    else:
                        importantword = False

                    if importantWord:                                               # if an important word is found, add it to the concept graph
                        association = inputAsWords[count2]
                        proximity = count2 - count1
                        conceptgen.addconcept(noun, associationType, association, proximity)

                for count3 in range(0, count1):                                     # looks for important word before noun
                    importantWord = True
                    if inputAsPartsOfSpeech[count3] in nounCodes:
                        associationType = 0
                    elif inputAsPartsOfSpeech[count3] in verbCodes:
                        associationType = 1
                    elif inputAsPartsOfSpeech[count3] in adjectiveCodes:
                        associationType = 2
                    else:
                        importantWord = False

                    if importantWord:                                               # if an important word is found, add it to the concept graph
                        association = inputAsWords[count3]
                        proximity = count1 - count3
                        conceptgen.addconcept(noun, associationType, association, proximity)
                else:
                    pass                                                            # naughty words get put in the word passer to atone for their sins

conceptreader(inputAsWords, inputAsPartsOfSpeech)