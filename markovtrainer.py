# Name:             Sentence Template Markov model Trainer
# Description:      Trains the sentenestructure database on sentence chunks parsed from our input data
# Section:          LEARNING
import random

import sqlite3 as sql
from config import database
from colorama import init, Fore
init(autoreset = True)

connection = sql.connect(database['path'])
cursor = connection.cursor()

def train(wordInfo):
    print "Analyzing sentence structure..."
    # package things up to be added to the sentence structure model
    for count, word in enumerate(wordInfo):
        # so that we don't go out of bounds
        if count == 0:
            isSentenceStarter = 1
        else:
            isSentenceStarter = 0
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
                            # todo: should weight have a similar score formula to the one we use for associations?
                            weight = int(row[2]) + 1
                            cursor.execute('UPDATE sentencestructuremodel SET weight = \'%s\', is_sentence_starter = \'%s\' WHERE stem = \'%s\' AND leaf = \'%s\';' % (weight, isSentenceStarter, stemAsString, leafAsString))
                    else:
                        # otherwise, add the new stuff to the sentence model
                        print Fore.MAGENTA + "New chunk pattern found (%s, %s)! Adding..." % (stemAsString, leafAsString)
                        cursor.execute('INSERT INTO sentencestructuremodel VALUES (\'%s\', \'%s\', 1, \'%s\');' % (stemAsString, leafAsString, isSentenceStarter))