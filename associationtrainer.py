# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import numpy as np

import sqlite3 as sql

import utilities

connection = sql.connect('emma.db')
cursor = connection.cursor()
def find_associations(sentence):
    # todo: optimize after we get all the core association types in
    # todo: prefer proper nouns when we look for nouns
    # todo: check for "not" after word, give negative association
    for count, word in enumerate(sentence):
        with connection:
            cursor.execute('SELECT word FROM dictionary WHERE is_banned = 1')
            bannedWords = cursor.fetchall()
        if word[0] not in bannedWords and word[1] != "FW":      # Don't store banned or foreign words
            # Types 1 & 2
            if word[0] == "be":
                if count != 0 and count != len(sentence) - 1:
                    prevWord = sentence[count - 1]
                    nextWord = sentence[count + 1]
                    if "NP" in prevWord[2]:
                        # Type 1
                        if "ADJP" in nextWord[2]:
                            print u"Found association: %s IS-PROPERTY-OF %s." % (nextWord[0], prevWord[0])
                            add_association(nextWord[0], prevWord[0], "IS-PROPERTY-OF")
                        # Type 2
                        elif "NP" in nextWord[2]:
                            for i in range(len(sentence)):
                                if count + (i + 1) <= len(sentence) - 1:
                                    chunksCountingForward = sentence[count + (i + 1)]
                                    if chunksCountingForward[1] in utilities.nounCodes:
                                        print u"Found association: %s IS-A %s." % (prevWord[0], chunksCountingForward[0])
                                        add_association(prevWord[0], chunksCountingForward[0], "IS-A")
                                        break
                                
            # Type 3
            if "NP" in word[2]:
                NPchunk = []
                for i in range(count):
                    if len(sentence) - (count - (i + 1)) >= 0:
                        chunksCountingBackward = sentence[count - (i + 1)]
                        # todo: add catch for ADJP in case input lists adjectives (ex. "the big, white, round orb")
                        if "B" in chunksCountingBackward[2]:
                            NPchunk.extend(sentence[count - (i + 1):count])
                            break
                for group in NPchunk:
                    if group[1] in utilities.adjectiveCodes and group[0]:
                        print u"Found association: %s IS-PROPERTY-OF %s." % (group[0], word[0])
                        add_association(group[0], word[0], "IS-PROPERTY-OF")

            # Types 4 & 5
            if "VP" in word[2] or "ADVP" in word[2]:
                if word[1] in utilities.adverbCodes:
                    # Type 4
                    if count != 0:
                        prevWord = sentence[count - 1]
                        if "VP" in prevWord[2]:
                            for i in range(count):
                                if len(sentence) - (count - (i + 1)) >= 0:
                                    chunksCountingBackward = sentence[count - (i + 1)]
                                    if chunksCountingBackward[1] in utilities.verbCodes:
                                        print u"Found association: %s IS-PROPERTY-OF %s." % (word[0], chunksCountingBackward[0])
                                        add_association(word[0], chunksCountingBackward[0], "IS-PROPERTY-OF")
                    # Type 5
                    if count != len(sentence) - 1:
                        nextWord = sentence[count + 1]
                        if "VP" in nextWord[2]:
                            for i in range(count):
                                    if count + (i + 1) <= len(sentence) - 1:
                                        chunksCountingForward = sentence[count + (i + 1)]
                                        if chunksCountingForward[1] in utilities.verbCodes:
                                            print u"Found association: %s IS-PROPERTY-OF %s." % (word[0], chunksCountingForward[0])
                                            add_association(word[0], chunksCountingForward[0], "IS-PROPERTY-OF")

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
                                    print u"Found association: %s HAS %s." % (prevWord[0], chunksCountingForward[0])
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
                                        print u"Found association: %s HAS-ABILITY-TO %s." % (nounChoice, chunksCountingForward[0])
                                        add_association(nounChoice, chunksCountingForward[0], "HAS-ABILITY-TO")
                                        break
                                    else: break

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
        currentWeight = np.log(currentWeight/(1-currentWeight))+rankingConstant
    else:
        currentWeight = 0
    currentWeight += 1
    weight = 1/(1+e**-(currentWeight-rankingConstant))
    return weight