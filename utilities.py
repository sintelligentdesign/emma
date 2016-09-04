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
    for count, parsedSentence in enumerate(parsedMessage):
        rawSentence = []
        for word in parsedSentence: rawSentence.append(word[0])
        rawSentence = ' '.join(rawSentence)

        if rawSentence[-1] in [u".", u",", u"!", u"?"]: rawSentence = rawSentence[:-2] + rawSentence[-1]
        rawSentence = rawSentence[0].upper() + rawSentence[1:]

        sentenceIntents = []
        if intents[count]['declarative']: sentenceIntents.append(u"DECLARATIVE")
        if intents[count]['interrogative']: sentenceIntents.append(u"INTERROGATIVE")
        if intents[count]['greeting']: sentenceIntents.append(u"GREETING")

        prettyUnderstanding += rawSentence + u" " + u"(" + u' '.join(sentenceIntents) + u")\n"
    prettyUnderstanding = u"Emma interpreted this message as:\n" + prettyUnderstanding
    return prettyUnderstanding