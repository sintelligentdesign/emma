# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import numpy as np
import re

import sqlite3 as sql

import utilities

connection = sql.connect('emma.db')
cursor = connection.cursor()
def find_associations(sentence):
    # todo: optimize after we get all the core association types in
    # todo: prefer proper nouns when we look for nouns
    for count, word in enumerate(sentence):
        with connection:
            cursor.execute('SELECT word FROM dictionary WHERE is_banned = 1')
            bannedWords = cursor.fetchall()
        if word[0] not in bannedWords and word[1] != "FW":      # Don't store banned or foreign words
            # Types 1 & 2
            if word[0] == "be":     # todo: add "can"?
                prevWord = sentence[count - 1]
                nextWord = sentence[count + 1]
                if "NP" in prevWord[2]:
                    if "ADJP" in nextWord[2]:
                        # Type 1
                        print "Found association: %s IS-PROPERTY-OF %s." % (nextWord[0], prevWord[0])
                        add_association(nextWord[0], prevWord[0], "IS-PROPERTY-OF")
                    elif "NP" in nextWord[2]:
                        for i in range(len(sentence)):
                            chunksCountingForward = sentence[count + i]
                            if chunksCountingForward[1] in utilities.nounCodes:
                                # Type 2
                                print "Found association: %s IS-A %s." % (prevWord[0], chunksCountingForward[0])
                                add_association(prevWord[0], chunksCountingForward[0], "IS-A")
                                break
                                
            # Type 3
            if "NP" in word[2] and word[1] in utilities.nounCodes:
                NPchunk = []
                for i in range(count):
                    chunksCountingBackward = sentence[count - (i + 1)]
                    chunksCountingBackward = chunksCountingBackward[2]
                    # todo: add catch for ADJP in case input lists adjectives
                    if "B" in chunksCountingBackward[0]:
                        NPchunk.extend(sentence[count - (i + 1):count])
                        break
                for group in NPchunk:
                    if group[1] in utilities.adjectiveCodes and group[0]:
                        print "Found association: %s IS-PROPERTY-OF %s." % (group[0], word[0])
                        add_association(group[0], word[0], "IS-PROPERTY-OF")

            # todo: Type 4

            # Type 5
            if "VP" in word[2] and word[1] in utilities.verbCodes:
                if count != (len(sentence) - 1): nextWord = sentence[count + 1]
                else: break
                if "ADVP" in nextWord[2]:
                    VPchunk = []
                    for i in range(count):
                        chunksCountingBackward = sentence[count - i]
                        chunksCountingBackward = chunksCountingBackward[2]
                        if "B" in chunksCountingBackward[0]:
                            VPchunk.extend(sentence[count - i:count + 1])
                            break
                        for group in VPchunk:
                            if group[1] in utilities.verbCodes:
                                print "Found association: %s IS-PROPERTY-OF %s." % (nextWord[0], group[0])
                                add_association(nextWord[0], group[0], "IS-PROPERTY-OF")

            # Type 6
            # todo: move up while optimizing
            if word[0] == "have":
                prevWord = sentence[count - 1]
                nextWord = sentence[count + 1]
                if "NP" in prevWord[2]:
                    if "NP" in nextWord[2]:
                        for i in range(len(sentence)):
                            if i < len(sentence) - count:
                                chunksCountingForward = sentence[count + i]
                                if chunksCountingForward[1] in utilities.nounCodes:
                                    print "Found association: %s HAS %s." % (prevWord[0], chunksCountingForward[0])
                                    add_association(prevWord[0], chunksCountingForward[0], "HAS")
                                    break

def add_association(word, target, associationType):
    with connection:
        cursor.execute('SELECT * FROM associationmodel WHERE word = \'%s\' AND target = \'%s\' AND association_type = \'%s\';' % (re.escape(word), re.escape(target), associationType))
        SQLReturn = cursor.fetchone()
    if SQLReturn:
        # update record
        newWeight = calculate_weight(True, SQLReturn[4])
        with connection:
            cursor.execute('UPDATE associationmodel SET weight = \'%s\' WHERE word = \'%s\' AND target = \'%s\' AND association_type = \'%s\';' % (newWeight, re.escape(word), re.escape(target), associationType))
    else:
        # add record
        weight = calculate_weight(False, None)
        with connection:
            cursor.execute('INSERT INTO associationmodel(word, association_type, target, weight) VALUES (\'%s\', \'%s\', \'%s\', \'%s\');' % (re.escape(word), associationType, re.escape(target), weight))
            
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