# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities
# todo: split into posessive references (his, its) and non-posessive references (him, they)

antecedents = [
    "he", "him", "his", "himself", 
    "she", "her", "hers", "herself", 
    "it", "its", "itself",      # todo: find a good way to handle "it's'"
    "they", "them", "their", "themself", "themselves"
    ]

def decode_references(sentence):
    lastUsedNoun = u""
    for count, word in enumerate(sentence):
        if word[1] in utilities.nounCodes:
            lastUsedNoun = word
        if word[0] in antecedents:
            if lastUsedNoun:
                print u"Replacing posessive pronoun \'%s\' with \'%s\'..." % (word[0], lastUsedNoun[0])
                lastUsedNoun = sentence[count]
            else:
                print u"No nouns found for anticedent \'%s\'!" % word[0]