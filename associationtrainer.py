# Name:             Association Trainer
# Description:      Finds and adds associations to Emma's association model
# Section:          LEARNING
import sqlite3 as sql

import utilities

def find_associations(sentence):
    for count, word in enumerate(sentence):
        # Types 1, & 2
        if "be" in word[0]:
            prevWord = sentence[count - 1]
            nextWord = sentence[count + 1]
            if "NP" in prevWord[2]:
                if "ADJP" in nextWord[2]:
                    print "type 1"
                elif "NP" in nextWord[2]:
                    print "type 2"
                    
        # Type 3
        if "NP" in word[2] and word[1] in utilities.nounCodes:
            NPchunk = []
            for i in range(count):
                chunksCountingBackward = sentence[count - (i + 1)]
                chunksCountingBackward = chunksCountingBackward[2]
                if "B" in chunksCountingBackward[0]:
                    NPchunk.extend(sentence[count - (i + 1):count])
                    break
            for group in NPchunk:
                if group[1] in utilities.adjectiveCodes:
                    print "type 3"

connection = sql.connect('emma.db')
cursor = connection.cursor()
def add_association(word, target, type):
    with connection:
        cursor.execute('SELECT * FROM associationmodel WHERE word = \'%s\' AND target = \'%s\' AND association_type = \'%s\';' % (word, target, type))
        SQLReturn = cursor.fetchall()
        if SQLReturn:
            # update record
        else:
            # add record