# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities
from colorama import init, Fore
init(autoreset = True)

pronouns = [
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "they", "them", "their", "theirs", "themself", "themselves",
    "it", "its", "itself"
]
def determine_references(message):
    lastUsedNoun = list
    for sentence in message:
        for count, word in enumerate(sentence):
            if word[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                lastUsedNoun = word

            elif word[0] in pronouns and lastUsedNoun != list:
                print Fore.GREEN + u"Replacing pronoun \'%s\' with \'%s\'..." % (word[0], lastUsedNoun[0])
                sentence[count] = lastUsedNoun

    return message

posessiveReferences = {u"you": u"emma", u"your": u"emma", u"yours": u"emma", u"myself": u"emma"}      # todo: add "'s" for posessives (your -> emma's) when we're able to do something with posessives

def determine_posessive_references(sentence, asker=""):
    if asker != "": posessiveReferences.update({u"me": asker, u"i": asker, u"my": asker, u"mine": asker, u"myself": asker})
    else: posessiveReferences.update({u"me": u"you", u"i": u"you", u"my": u"your", u"mine": u"yours", u"myself": u"yourself"})
    
    for count, word in enumerate(sentence):
        if word[0] in posessiveReferences.keys():
            replacementWord = posessiveReferences[word[0]]
            print Fore.GREEN + u"replacing posessive reference \'%s\' with \'%s\'..." % (word[0], replacementWord)
            word[0] = replacementWord
            word[1] = u"NNP"
    return sentence