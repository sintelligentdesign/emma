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
    # Rank the input sentence's tags

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
    reply = unpack_chunks(generate_chunks(), rank_tags(tokenizedMessage))
    return reply

def rank_tags(sentence):
    # Tallies how many of each type of part of speech are used to help us decide which to use in our reply
    print "Ranking tags..."
    nounBlock = [0, 0, 0, 0]
    verbBlock = [0, 0, 0, 0, 0, 0]
    adjectiveBlock = [0, 0, 0]
    adverbBlock = [0, 0, 0, 0]
    for word in sentence:
        if word[1] in utilities.nounCodes:
            for count, pos in enumerate(utilities.nounCodes):
                if word[1] == pos:
                    nounBlock[count] += 1
        elif word[1] in utilities.verbCodes:
            for count, pos in enumerate(utilities.verbCodes):
                if word[1] == pos:
                    verbBlock[count] += 1
        elif word[1] in utilities.adjectiveCodes:
            for count, pos in enumerate(utilities.adjectiveCodes):
                if word[1] == pos:
                    adjectiveBlock[count] += 1
        elif word[1] in utilities.adverbCodes:
            for count, pos in enumerate(utilities.adverbCodes):
                if word[1] == pos:
                    adverbBlock[count] += 1
    tagRanking = [nounBlock, verbBlock, adjectiveBlock, adverbBlock]
    return tagRanking

def generate_chunks():
    print "Generating sentence chunks..."
    # todo: detect loops?
    sentenceTemplate = []
    
    with connection:
        cursor.execute("SELECT stem FROM sentencestructuremodel WHERE is_sentence_starter = 1;")
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
        print "Generated template is too long. Regenerating..."
        sentenceTemplate = generate_chunks()
    return sentenceTemplate

def unpack_chunks(chunkList, tagRanking): 
    print "Getting parts of speech from generated chunks..."
    POSList = []
    nounChoice = ""
    verbChoice = ""
    adjectiveChoice = ""
    adverbChoice = ""
    # Noun pass
    m = max(tagRanking[0])
    rankedPosition = [i for i, j in enumerate(tagRanking[0]) if j == m]
    if len(rankedPosition) == 1:
        nounChoice = utilities.nounCodes[rankedPosition[0]]
    else:
        nounChoice = "NN"

    # Verb pass
    m = max(tagRanking[1])
    rankedPosition = [i for i, j in enumerate(tagRanking[1]) if j == m]
    if len(rankedPosition) == 1:
        verbChoice = utilities.verbCodes[rankedPosition[0]]
    else:
        verbChoice = "VB"

    # Adjective pass
    m = max(tagRanking[2])
    rankedPosition = [i for i, j in enumerate(tagRanking[2]) if j == m]
    if len(rankedPosition) == 1:
        adjectiveChoice = utilities.adjectiveCodes[rankedPosition[0]]
    else:
        adjectiveChoice = "JJ"

    # adverb Pass
    m = max(tagRanking[3])
    rankedPosition = [i for i, j in enumerate(tagRanking[3]) if j == m]
    if len(rankedPosition) == 1:
        adverbChoice = utilities.adverbCodes[rankedPosition[0]]
    else:
        adverbChoice = "RB"

    for chunk in chunkList:
        if "NP" in chunk:
            POSList.extend(["DT"] + [adverbChoice] + [adjectiveChoice] + [nounChoice] + ["PRP"])
        elif "PP" in chunk:
            POSList.extend(["TO", "IN"])
        elif "VP" in chunk:
            POSList.extend([adverbChoice] + ["MD"] + [verbChoice])
        elif "ADVP" in chunk:
            POSList.extend([adverbChoice])
        elif "ADJP" in chunk:
            POSList.extend(["CC"] + [adverbChoice] + [adjectiveChoice])
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