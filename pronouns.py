# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities
from config import console
from colorama import init, Fore
init(autoreset = True)

properPronouns = [
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "they", "them", "their", "theirs", "themself", "themselves"
]
otherPronouns = [
    "it", "its", "itself"
]

def determine_references(sentence):
    lastUsedProperNoun = ""
    lastUsedNoun = ""
    for count, word in enumerate(sentence):
        if word[1] in ['NN', 'NNS']: lastUsedNoun = word
        elif word[1] in ['NNP', 'NNPS']: 
            lastUsedProperNoun = word
            if lastUsedNoun = "": lastUsedNoun = word

        if word[0] in properPronouns and lastUsedProperNoun != "":
            print Fore.GREEN + u"Replacing proper pronoun \'%s\' with \'%s\'..." % (word[0], lastUsedProperNoun[0])
            sentence[count] = lastUsedProperNoun
        elif word[0] in otherPronouns and lastUsedNoun != "":
            print Fore.GREEN + u"Replacing pronoun \'%s\' with \'%s\'..." % (word[0], lastUsedNoun[0])
            sentence[count] = lastUsedNoun

    return sentence

posessiveReferences = {u"you": u"emma", u"your": u"emma", u"yours": u"emma", u"myself": u"emma"}      # todo: add apostrophe + s when we're able to handle it

def flip_posessive_references(sentence, asker=""):
    if asker != "": posessiveReferences.update({u"me": asker, u"i": asker, u"my": asker, u"mine": asker, u"myself": asker})
    else: posessiveReferences.update({u"me": u"you", u"i": u"you", u"my": u"your", u"mine": u"yours", u"myself": u"yourself"})
    
    for count, word in enumerate(sentence):
        if word[0] in posessiveReferences:
            replacementWord = posessiveReferences[word[0]]
            print Fore.GREEN + u"replacing posessive reference \'%s\' with \'%s\'..." % (word[0], replacementWord)
            word[0] = replacementWord
            word[1] = "NNP"
    return sentence