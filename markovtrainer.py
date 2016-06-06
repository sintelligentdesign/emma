# Name:             Sentence Template Markov model Trainer
# Description:      Trains the sentenestructure database on sentence chunks parsed from our input data
# Section:          LEARNING
import random
import sqlite3 as sql

connection = sql.connect('emma.db')
cursor = connection.cursor()

def train(wordInfo):
    print "Analyzing sentence structure..."
    # package things up to be added to the sentence structure model
    for count, word in enumerate(wordInfo):
        # so that we don't go out of bounds
        if count < len(wordInfo) - 3:
            # get the stem and leaf
            secondWord = wordInfo[count + 1]
            thirdWord = wordInfo[count + 2]
            fourthWord = wordInfo[count + 3]
            stemAsString = word[2] + ' ' + secondWord[2] + ' ' + thirdWord[2]
            leafAsString = fourthWord[2]
            
            if "O" not in stemAsString:
                # if the stem doesn't include a sentence ending character, fetched saved stems
                with connection:
                    cursor.execute('SELECT * FROM sentencestructuremodel WHERE stem = \'%s\';' % stemAsString)
                    SQLReturn = cursor.fetchall()
                
                    # see if we're adding a duplicate stem
                    if SQLReturn:
                        # if it is, check if the leaf is the same
                        savedLeaves = []
                        for row in SQLReturn:
                            savedLeaves.append(row[1])
                        if leafAsString in savedLeaves:
                            # if this is an existing building block, increment its weight
                            # todo: find a better scoring system
                            weight = int(row[2]) + 1
                            cursor.execute('UPDATE sentencestructuremodel SET weight = \'%s\' WHERE stem = \'%s\' AND leaf = \'%s\';' % (weight, stemAsString, leafAsString))
                    else:
                        # otherwise, add the new stuff to the sentence model
                        print "New chunk pattern found (%s, %s)! Adding..." % (stemAsString, leafAsString)
                        cursor.execute('INSERT INTO sentencestructuremodel VALUES (\'%s\', \'%s\', 1);' % (stemAsString, leafAsString))