# Name:             Sentence Layout Generator
# Description:      Generates sentence layout templates from our Markov model of sentence chunks
# Section:          REPLY
# Writes/reads:     
# Dependencies:     random, ast, sqlite3
# Dependency of:    
import random
import ast

import sqlite3 as sql

connection = sql.connect('emma.db')
cursor = connection.cursor()

def generate():
    print "Generating sentence chunks..."
    # todo: fix bug where generation hangs randomly
    sentenceTemplate = []
    
    with connection:
        cursor.execute("SELECT stem FROM sentencestructuremodel;")
        SQLReturn = cursor.fetchall()
        SQLReturn = random.choice(SQLReturn)
    stem = SQLReturn
    stem = stem[0]
    stem = str(stem)
    stem = stem.split()
    sentenceTemplate.extend(stem)
    
    while sentenceTemplate[-1] not in ['O']:
        stem = sentenceTemplate[-3:]
        with connection:
            cursor.execute("SELECT * FROM sentencestructuremodel WHERE stem = '%s';" % " ".join(stem))
            stemRows = cursor.fetchall()
        weights = []
        possibleLeaves = []
        for row in stemRows:
            weights.append(row[2])
            possibleLeaves.append(row[1])
        # choose a leaf based on weighted die roll
        die = random.randint(0, sum(weights))
        dieValue = 0
        nextChunk = ""
        for count, weight in enumerate(weights):
            if die >= dieValue:
                nextChunk = possibleLeaves[count]
                dieValue += weight
        if nextChunk:
            sentenceTemplate.append(nextChunk)
    print "Sentence chunks: " + " ".join(sentenceTemplate)