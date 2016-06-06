# Name:             Sentence Layout Generator
# Description:      Generates sentence layout templates from our Markov model of sentence chunks
# Section:          REPLY
import random
import ast

import sqlite3 as sql

connection = sql.connect('emma.db')
cursor = connection.cursor()

maxSentenceLength = 7

def generate():
    print "Generating sentence chunks..."
    # todo: detect loops?
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
    
    while sentenceTemplate[-1] not in ['O'] and len(sentenceTemplate) < maxSentenceLength:
        stem = sentenceTemplate[-3:]
        with connection:
            cursor.execute("SELECT * FROM sentencestructuremodel WHERE stem = '%s';" % " ".join(stem))
            stemRows = cursor.fetchall()
        weights = []
        possibleLeaves = []
        if stemRows:
            for row in stemRows:
                weights.append(row[2])
                possibleLeaves.append(row[1])
        else:
            sentenceTemplate.append("%")
            print "No leaves for current stem! Regenerating..."
            sentenceTemplate = generate()
            break
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
    if len(sentenceTemplate) >= maxSentenceLength:
        print "Generated template is too long. Regnerating..."
        sentenceTemplate = generate()
    return sentenceTemplate