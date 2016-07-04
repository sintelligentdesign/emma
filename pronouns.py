# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities
from config import console
from colorama import init, Fore
init(autoreset = True)

subordinatePronouns = [
    "he", "him", "himself",
    "she", "herself",
    "it", "itself",
    "they", "them", "themself", "themselves"
    ]
posessivePronouns = [
    "his", 
    "her", "hers",
    "its",
    "their", "theirs"
    ]

def determine_references(sentence):
    # todo: work differently with proper nouns?
    # todo: How should this work for references that refer to words in previous sentences?
    lastUsedNoun = ""
    for count, word in enumerate(sentence):
        if word[1] in utilities.nounCodes: lastUsedNoun = word
        elif word[0] in subordinatePronouns + posessivePronouns:
            if lastUsedNoun != "":
                print Fore.GREEN + u"Replacing pronoun \'%s\' with \'%s\'..." % (word[0], lastUsedNoun[0])
                sentence[count] = lastUsedNoun
            else: print Fore.YELLOW + u"No nouns found for pronoun \'%s\'!" % word[0]

posessiveReferences = {u"you": u"emma", u"your": u"emma\'s", u"yours": u"emma\'s", u"myself": u"emma"}

def flip_posessive_references(sentence, asker=""):
    if asker != "": posessiveReferences.update({u"me": asker, u"i": asker, u"my": asker + u"\'s", u"mine": asker + u"\'s", u"myself": asker})
    else: posessiveReferences.update({u"me": u"you", u"i": u"you", u"my": u"your", u"mine": u"yours", u"myself": u"yourself"})
    
    for count, word in enumerate(sentence):
        if word[0] in posessiveReferences:
            replacementWord = posessiveReferences[word[0]]
            print Fore.GREEN + u"replacing posessive reference \'%s\' with \'%s\'..." % (word[0], replacementWord)
            word[0] = replacementWord
            word[1] = "NNP"
    return sentence