# -*- coding: utf-8 -*-
# Name:             Utilities
# Description:      Miscellaneous functions and vars
# Section:

from colorama import init, Fore
init(autoreset = True)

# Auxillary functions classify POS
nounCodes = ['NN', 'NNS', 'NNP', 'NNPS']
verbCodes = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
adjectiveCodes = ['JJ', 'JJR', 'JJS']
adverbCodes = ['RB', 'RBR', 'RBS', 'RP']

# Turn Emma's understanding and asker intents into something that people can read for Tumblr
def pretty_print_understanding(parsedMessage, intents):
    print "Formatting Emma's understanding for Tumblr..."
    prettyUnderstanding = ""
    for count, sentence in enumerate(parsedMessage):
        rawSentence = []
        for word in parsedMessage: rawSentence.append(word[0])
        rawSentence = ' '.join(rawSentence)

        for count, word in enumerate(rawSentence):
            if word[0] in [u".", u",", u"!", u"?"]:
                reply[count - 1][0] += word[0]
                del reply[count]

        rawSentence[0] = rawSentence[0][0].upper() + rawSentence[0][1:]

        sentenceIntents = []
        if intents[count]['declarative'] == True: sentenceIntents.append(u"DECLARATIVE")
        if intents[count]['interrogative'] == True: sentenceIntents.append(u"INTERROGATIVE")
        if intents[count]['greeting'] == True: sentenceIntents.append(u"GREETING")

        prettyUnderstanding += u' '.join(rawSentence) + u" " + u"(" + u' '.join(sentenceIntents) + u")\n"

    prettyUnderstanding = u"Emma interpreted this message as:\n" + prettyUnderstanding
    return prettyUnderstanding