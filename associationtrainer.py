# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import numpy as np
import re

import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import utilities

connection = sql.connect('emma.db')
cursor = connection.cursor()
def find_associations(sentence):
    for count, word in enumerate(sentence):
        if word[1]  not in ["LS", "SYM", "UH", ".", ",", ":", "(", ")", "FW"]:      # Don't associate unusable parts of speech
            if count != 0 and count - 1 != len(sentence):
                # Make lists out of the words before and after the word that we're on
                wordsBackward = sentence[0:count]
                wordsForeward = sentence[count + 1:-1]

                ## Look for keywords
                if word[0] == "be":
                    if "NP" in wordsBackward[-1][2] and "ADJP" in wordsForeward[0][2] or "NP" in wordsForeward[0][2]:
                        for nextWord in wordsForeward:
                            # NP + 'be' + ADJP >> NN HAS-PROPERTY JJ (milk is white >> milk HAS-PROPERTY white)
                            if nextWord[1] in utilities.adjectiveCodes: add_association(wordsBackward[-1][0], nextWord[0], "HAS-PROPERTY")

                            # NP + 'be' + NP >> NN IS-A NN (a dog is an animal >> dog IS-A animal) 
                            elif nextWord[1] in utilities.nounCodes: 
                                add_association(wordsBackward[-1][0], nextWord[0], "IS-A")
                                break

                            elif "NP" in nextWord[2] or nextWord[0] == "and": continue
                            # catch us if we go over because of incorrect sentence parsing
                            else: break

                if "NP" in word[2] and word[1] in utilities.nounCodes:
                    for prevWord in reversed(wordsBackward):        # NP containing JJ + NN >> NN HAS-PROPERTY JJ (the big house >> house HAS-PROPERTY big)
                        if prevWord[1] in utilities.adjectiveCodes: add_association(word[0], prevWord[0], "HAS-PROPERTY")
                        else: break

                    for nextWord in wordsForeward:      # NP + VP >> NN HAS-ABILITY-TO VB (Cats can run fast >> cat HAS-ABILITY-TO run)
                        if "VP" in nextWord[2] and nextWord[1] in utilities.verbCodes and nextWord[0] != "be": add_association(word[0], nextWord[0], "HAS-ABILITY-TO")
                        elif "NP" not in nextWord[2]: break

                if word[1] in utilities.verbCodes:
                    if wordsBackward != [] and wordsBackward[-1][1] in utilities.adverbCodes:       # VP containing RB + VB >> RB HAS-PROPERTY VB (It quickly moves >> quickly HAS-PROPERTY moves)
                        for prevWord in reversed(wordsBackward):
                            if prevWord[1] in utilities.adverbCodes: add_association(word[0], prevWord[0], "HAS-PROPERTY")

                    if wordsForeward != [] and "VP" in wordsForeward[0][1]:     # VP + ADJP >> VB HAS-PROPERTY RB (Cats can run fast >> run HAS-PROPERTY fast)
                        for nextWord in wordsForeward:
                            if nextWord[1] in utilities.adverbCodes or nextWord[1] in utilities.verbCodes: add_association(word[0], nextWord[0], "HAS-PROPERTY")

                # NP + 'has' + NP >> NN HAS NN (People have two hands >> People HAS hands)
                if word[0] == "have" and "NP" in wordsBackward[-1][2] and "NP" in wordsForeward[0][2]:
                    subjectNoun = ""
                    targetNoun = ""
                    for word in reversed(wordsBackward):
                        if word[1] in utilities.nounCodes:
                            subjectNoun = word[0]
                            break

                    for word in wordsForewardward:
                        if word[1] in utilities.nounCodes:
                            targetNoun = word[0]
                            break

                    if subjectNoun != "" and targetNoun != "": add_association(subjectNoun, targetNoun, "HAS")

                # VB + obj >> VB HAS-OBJECT NN (This button releases the hounds. >> release HAS-OBJECT hound)
                if "OBJ" in word[3] and word[1] in utilities.nounCodes:
                    for otherWord in sentence:
                        if otherWord[1] in utilities.verbCodes: add_association(otherWord[0], word[0], "HAS-OBJECT")

def add_association(word, target, associationType):
    word = re.escape(word)
    with connection:
        cursor.execute('SELECT * FROM associationmodel WHERE word = \"%s\" AND target = \"%s\" AND association_type = \"%s\";' % (word.encode('utf-8'), target.encode('utf-8'), associationType))
        SQLReturn = cursor.fetchone()
    if SQLReturn:
        # update record
        print Fore.MAGENTA + u"Strengthened association: %s %s %s." % (word, associationType, target)
        newWeight = calculate_new_weight(SQLReturn[3])
        with connection: cursor.execute('UPDATE associationmodel SET weight = \'%s\' WHERE word = \"%s\" AND target = \"%s\" AND association_type = \'%s\';' % (newWeight, word.encode('utf-8'), target.encode('utf-8'), associationType))
    else:
        # add record
        print Fore.MAGENTA + u"Found new association: %s %s %s." % (word, associationType, target)
        weight = 0.0999999999997        # This is what the weight calculates to for all new associations, so why waste cycles calculating
        with connection: cursor.execute('INSERT INTO associationmodel(word, association_type, target, weight) VALUES (\"%s\", \'%s\', \"%s\", \'%s\');' % (word.encode('utf-8'), associationType, target.encode('utf-8'), weight))

e = np.exp(1)
def calculate_new_weight(currentWeight):
    rankingConstant = 4.19722457734

    if currentWeight == 1: currentWeight = 0.999999999994
    occurances = np.log(currentWeight/(1-currentWeight))+rankingConstant     # turn the weight back into the number of occurances of the association
    occurances += 1

    weight = 1/(1+e**-(occurances-rankingConstant))      # re-calculate weight
    return weight