# Name:             Sentence Generator
# Description:      Generates sentences based on what Emma knows about English and the world
# Section:          REPLY
import random
import ast

import sqlite3 as sql

import utilities

connection = sql.connect('emma.db')
cursor = connection.cursor()

maxSentenceLength = 7

def generate_sentence(tokenizedMessage):
    # Find important words in the sentence
    importantWords = []
    for word in tokenizedMessage:
        if word[1] in utilities.nounCodes and word[3]:
            importantWords.append(word[0])
    print "Important words: " + str(importantWords)

    # find words related to the important words
    depth1 = []
    depth2 = []
    relatedWords = []
    for word in importantWords:
        depth1.extend(find_related_words(word))
    for word in depth1:
        depth2.extend(find_related_words(word[0]))
        relatedWords.extend(word)
    for word in depth2:
        relatedWords.extend(word)
    print "Related words: " + str(relatedWords)

    # Reply to message
    print "Creating reply..."
    reply = unpack_chunks(generate_chunks())

def generate_chunks():
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
            sentenceTemplate = generate_chunks()
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
        sentenceTemplate = generate_chunks()
    return sentenceTemplate

def unpack_chunks(): 
    print "Getting parts of speech from generated chunks..."
    # todo: use sentence parts of speech to choose which code to use when filling in sentences
    POSList = []
    for chunk in chunkList:
        if "NP" in chunk:
            POSList.extend(["DT"] + utilities.adverbCodes + utilities.adjectiveCodes + utilities.nounCodes + ["PRP"])
        elif "PP" in chunk:
            POSList.extend(["TO", "IN"])
        elif "VP" in chunk:
            POSList.extend(utilities.adverbCodes + ["MD"] + utilities.verbCodes)
        elif "ADVP" in chunk:
            POSList.extend(utilities.adverbCodes)
        elif "ADJP" in chunk:
            POSList.extend(["CC"] + utilities.adverbCodes + utilities.adjectiveCodes)
        elif "SBAR" in chunk:
            POSList.extend(["IN"])
        elif "PRT" in chunk:
            POSList.extend(["RP"])
        elif "INTJ" in chunk:
            POSList.extend(["UH"])
    return POSList

def find_related_words(word):
    relatedWords = []
    relatedWord = ()
    with connection:
        cursor.execute('SELECT target, association_type, weight FROM associationmodel WHERE word = \'%s\';' % word)
        SQLReturn = cursor.fetchall()
    for row in SQLReturn:
        relatedWord = (row[0], row[1], row[2])
        if relatedWord != ():
            relatedWords.append(relatedWord)
    # todo: remove dupes
    return relatedWords