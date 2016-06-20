# Name:             Antecedent Filler
# Description:      Replaces words like "it" or "they" with the nouns that they refer to
# Section:          
import utilities
from config import console
from colorama import init, Fore
init(autoreset = True)

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

def determine_references(sentence):
    # (last used noun, is it proper y/n)
    # todo: work differently with proper nouns
    # todo: maybe do something different if the noun is tagged as a subject/object?
    lastUsedNouns = []
    for count, word in enumerate(sentence):
        if word[1] in utilities.nounCodes:
            if word[1] in ["NNP", "NNPS"]: lastUsedNouns.append((word, True))
            else: lastUsedNouns.append((word, False))

        if word[0] in subordinateReferences or word[0] in posessiveReferences:
            replacementSuccessful = False
            if lastUsedNouns:
                for noun in reversed(lastUsedNouns):
                    if noun[1] == False:
                        replacement = noun[0]
                        print Fore.GREEN + u"Replacing pronoun \'%s\' with \'%s\'..." % (word[0], replacement[0])
                        sentence[count] = replacement
                        replacementSuccessful = True
            if replacementSuccessful == False:
                print Fore.YELLOW + u"No nouns found for pronoun \'%s\'!" % word[0]

def flip_posessive_references(sentence, asker):
    posessiveReferences = {"you": "emma", "your": "my", "yours": "mine", "myself": "yourself"}
    if asker: posessiveReferences.update({"me": asker, "i": asker, "my": asker + u"\'s", "mine": asker + u"\'s", "myself": asker})
    else: posessiveReferences.update({"me": "you", "i": "you", "my": "your", "mine": "yours", "myself": "yourself"})        # todo: if we don't have an asker, should we have some other word? Perhaps 'someone'?
    
    for count, word in enumerate(sentence):
        if word[0] in posessiveReferences:
            replacementWord = posessiveReferences.get(word[0])
            print Fore.GREEN + u"replacing posessive reference \'%s\' with \'%s\'..." % (word[0], replacementWord)
            word[0] = replacementWord
    return sentence