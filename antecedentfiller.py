# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities

# todo: this module is a good idea, but it's really rough and probably better for a ~1.1 or 1.2 feature

antecedents = [
    "he", "him", "his", "himself", 
    "she", "her", "hers", "herself", 
    "it", "its", "itself",      # todo: find a good way to handle "it's'"
    "they", "them", "their", "themself", "themselves"
    ]
    
def determine_references(sentence):
    for count, word in enumerate(sentence):
        if word[0] in antecedents:
            for i in range(count):
                wordsCountingBackward = sentence[count - (i + 1)]
                if wordsCountingBackward[1] in utilities.nounCodes:
                    print "Replacing antecedent \'%s\' with \'%s\'..." % (word[0], wordsCountingBackward[0])
                    sentence[count] = (wordsCountingBackward[0], wordsCountingBackward[1], wordsCountingBackward[2], wordsCountingBackward[3])
                    break
                elif i == count:
                    print "No nouns found for antecedent \'%s\'." % word[0]
                    break