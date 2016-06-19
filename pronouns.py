# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities

# todo: finish this and fix the bugs and stuff

subordinateReferences = [
    "he", "him", "himself",
    "she", "herself",
    "its", "itself",
    "they", "them", "themself", "themselves"
    ]
posessiveReferences = [
    "his", 
    "her", "hers",
    "its",      # "it's" is a special case
    "their", "theirs"
    ]

posessiveReferences = {
    "me": "you", "i": "you", "my": "your", "mine": "yours", "myself": "yourself", 
              "you": "emma", "your": "my", "yours": "mine", "myself": "yourself"
    }

def decode_references(sentence):
    lastUsedNouns = []
    for count, word in enumerate(sentence):
        if word[1] in utilities.nounCodes:
            if word[1] in ["NNP", "NNPS"]: lastUsedNouns.append((word, True))
            else: lastUsedNouns.append((word, False))

        if word[0] in subordinateReferences:
            replacementSuccessful = False
            if lastUsedNouns:
                for noun in reversed(lastUsedNouns):
                    if noun[1] == False:
                        word = noun[0]
                        print u"Replacing pronoun \'%s\' with \'%s\'..." % (word[0], noun[0])
                        sentence[count] = word
                        replacementSuccessful = True
            if replacementSuccessful == False:
                print u"No nouns found for pronoun \'%s\'!" % word[0]

def flip_posessive_references(sentence):
    for count, word in enumerate(sentence):
        if word[0] in posessiveReferences.keys():
            replacementWord = posessiveReferences.get(word[0])
            print u"replacing posessive reference \'%s\' with \'%s\'..." % (word[0], replacementWord)
            sentence[count] = (replacementWord, word[1], word[2], word[3])      # todo: is there a better way to do this?
    return sentence