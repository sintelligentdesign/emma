# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import numpy as np

import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import utilities
from config import database

connection = sql.connect(database['path'])
cursor = connection.cursor()
def find_associations(sentence):
    # todo: optimize after we get all the core association types in
    # todo: prefer proper nouns when we look for nouns
    # todo: check for "not" after word, give negative association
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_banned = 1')
        bannedWords = cursor.fetchall()

    for count, word in enumerate(sentence):
        wordsBack = sentence[0:count]
        wordsFore = sentence[count + 1:-1]
        if count != 0 and count != len(sentence): wordSandwich = True
        else: wordSandwich = False

        if word[0] not in bannedWords and word[1]  not in ["LS", "SYM", "UH", ".", ",", ":", "(", ")", "FW"]:      # Don't associate banned words or unusable parts of speech
            # Types 1 & 2
            if wordSandwich:
                if word[0] == "be":
                    if "NP" in wordsBack[-1][2] and "ADJP" in wordsFore[0][2] or "NP" in wordsFore[0][2]:
                        for nextWord in wordsFore:
                            if nextWord[1] in utilities.adjectiveCodes:     # Type 1
                                print Fore.MAGENTA + u"Found association: %s IS-PROPERTY-OF %s." % (wordsBack[-1][0], nextWord[0])
                                add_association(wordsBack[-1][0], nextWord[0], "IS-PROPERTY-OF")
                            elif nextWord[1] in utilities.nounCodes:        # Type 2
                                print Fore.MAGENTA + u"Found association: %s IS-A %s." % (wordsBack[-1][0], nextWord[0])
                                add_association(wordsBack[-1][0], nextWord[0], "IS-A")
                                break
                            # catch us if we go over because of incorrect sentence parsing
                            else: break

            # Type 3
            if "NP" in word[2] and word[1] in utilities.nounCodes:
                print word
                for prevWord in reversed(wordsBack):
                    if prevWord[1] in utilities.adjectiveCodes:
                        print Fore.MAGENTA + u"Found association: %s IS-PROPERTY-OF %s." % (prevWord[0], word[0])
                        add_association(prevWord[0], word[0], "IS-PROPERTY-OF")
                    else: break

            # Types 4 & 5
            if word[1] in utilities.verbCodes:
                if wordsBack[-1][1] in utilities.adverbCodes:       # Type 4
                    for prevWord in reversed(wordsBack):
                        if prevWord[1] in utilities.adverbCodes:
                            print Fore.MAGENTA + u"Found association: %s IS-PROPERTY-OF %s." % (prevWord[0], word[0])
                            add_association(prevWord[0], word[0], "IS-PROPERTY-OF")
                if "VP" in wordsFore[0][1]:     # Type 5
                    for nextWord in wordsFore:
                        if nextWord[1] in utilities.adverbCodes or nextWord[1] in utilities.verbCodes:
                            print Fore.MAGENTA + u"Found association: %s IS-PROPERTY-OF %s." % (prevWord[0], word[0])
                            add_association(nextWord[0], word[0], "IS-PROPERTY-OF")

            # Type 6
            if word[0] == "have":
                prevWord = sentence[count - 1]
                nextWord = sentence[count + 1]
                if "NP" in prevWord[2]:
                    if "NP" in nextWord[2]:
                        for i in range(len(sentence)):
                            if count + (i + 1) <= len(sentence) - 1:
                                chunksCountingForward = sentence[count + i]
                                if chunksCountingForward[1] in utilities.nounCodes:
                                    print Fore.MAGENTA + u"Found association: %s HAS %s." % (prevWord[0], chunksCountingForward[0])
                                    add_association(prevWord[0], chunksCountingForward[0], "HAS")
                                    break

            # Type 7
            # todo: for optimization purposes, have this and type 3 in the same function
            if "NP" in word[2]:
                if count != (len(sentence) - 1):nextWord = sentence[count + 1]
                else: break
                if "VP" in nextWord[2]:
                    nounChoice = ""
                    for i in range(count + 1):
                        chunksCountingBackward = sentence[count - i]
                        if chunksCountingBackward[1] in utilities.nounCodes:
                            nounChoice = chunksCountingBackward[0]
                            break
                    if nounChoice != "":        # todo: find out why nounChoice sometimes is blank and fix it
                        for i in range(len(sentence)):
                            if i < len(sentence) - count:
                                chunksCountingForward = sentence[count + i]
                                if chunksCountingForward[1] in utilities.verbCodes:
                                    if chunksCountingForward[0] != "be":
                                        print Fore.MAGENTA + u"Found association: %s HAS-ABILITY-TO %s." % (nounChoice, chunksCountingForward[0])
                                        add_association(nounChoice, chunksCountingForward[0], "HAS-ABILITY-TO")
                                        break
                                    else: break

            # Type 10
            if "OBJ" in word[3] and word[1] in utilities.nounCodes:
                for otherWord in sentence:
                    if otherWord[1] in utilities.verbCodes:
                        print Fore.MAGENTA + u"Found association: %s IS-OBJECT-OF %s." % (word[0], otherWord[0])
                        add_association(word[0], otherWord[0], "IS-OBJECT-OF")

def add_association(word, target, associationType):
    with connection:
        cursor.execute('SELECT * FROM associationmodel WHERE word = \"%s\" AND target = \"%s\" AND association_type = \"%s\";' % (word.encode('utf-8'), target.encode('utf-8'), associationType))
        SQLReturn = cursor.fetchone()
    if SQLReturn:
        # update record
        newWeight = calculate_weight(True, SQLReturn[3])
        with connection:
            cursor.execute('UPDATE associationmodel SET weight = \'%s\' WHERE word = \"%s\" AND target = \"%s\" AND association_type = \'%s\';' % (newWeight, word.encode('utf-8'), target.encode('utf-8'), associationType))
    else:
        # add record
        weight = calculate_weight(False, None)
        with connection:
            cursor.execute('INSERT INTO associationmodel(word, association_type, target, weight) VALUES (\"%s\", \'%s\', \"%s\", \'%s\');' % (word.encode('utf-8'), associationType, target.encode('utf-8'), weight))

e = np.exp(1)
def calculate_weight(isUpdate, currentWeight):
    rankingConstant = 3.19722457734
    if isUpdate == True:
        if currentWeight == 1: currentWeight = 0.9999999999999      # todo: this is a bad fix and we should do something better
        currentWeight = np.log(currentWeight/(1-currentWeight))+rankingConstant
    else:
        currentWeight = 0
    currentWeight += 1
    weight = 1/(1+e**-(currentWeight-rankingConstant))
    return weight
