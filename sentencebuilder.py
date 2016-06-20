# Name:             Sentence Generator
# Description:      Generates sentences based on what Emma knows about English and the world
# Section:          REPLY
import random

import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import utilities
from config import console, database

connection = sql.connect(database['path'])
cursor = connection.cursor()

maxSentenceLength = 7

def generate_sentence(tokenizedMessage):
    # Rank the input sentence's tags

    # Find important words in the sentence
    importantWords = []
    for word in tokenizedMessage:
        if word[1] in utilities.nounCodes and word[3]:
            importantWords.append(word[0])
    if console['verboseLogging']: print Fore.MAGENTA + u"Important words: " + str(importantWords)

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
    if console['verboseLogging']: print Fore.MAGENTA + u"Related words: " + str(relatedWords)

    # Reply to message
    print "Creating reply..."
    reply = fill_simple_pos(unpack_chunks(generate_chunks(), rank_tags(tokenizedMessage)))
    return reply, importantWords, relatedWords

def find_related_words(word):
    relatedWords = []
    with connection:
        cursor.execute("SELECT word, association_type, target, weight FROM associationmodel WHERE word = \"%s\" OR target = \"%s\";" % (word.encode('utf-8'), word.encode('utf-8')))
        SQLReturn = cursor.fetchall()
    for row in SQLReturn:
        relatedWord = (row[0], row[1], row[2], row[3])
        relatedWords.append(relatedWord)
    # todo: remove duplicates
    if console['verboseLogging']: print Fore.MAGENTA + u"Found %d related words for %s" % (len(relatedWords), word)
    return relatedWords

def rank_tags(sentence):
    # Tallies how many of each type of part of speech are used to help us decide which to use in our reply
    if console['verboseLogging']: print "Ranking tags..."
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
    if console['verboseLogging']: print "Generating sentence chunks..."
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
    
    attemptCount = 0
    while attemptCount < 10 and sentenceTemplate[-1] not in ['O'] and len(sentenceTemplate) < maxSentenceLength:        # todo: i figure that 10 attempts is a good number, but do we want to do more?
    # todo: if generation fails, find a better way to retry than running the function again
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
            if console['verboseLogging']: print Fore.YELLOW + "No leaves for current stem! Regenerating..."
            attemptCount += 1
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
        if console['verboseLogging']: print Fore.YELLOW + "Generated template is too long. Regenerating..."
        attemptCount += 1
        sentenceTemplate = generate_chunks()
    if sentenceTemplate[-1] != "O":
        if console['verboseLogging']: print Fore.Yellow + "Invalid ending chunk. Regenerating..."
        attemptCount += 1
        sentenceTemplate = generate_chunks()
    return sentenceTemplate

def unpack_chunks(chunkList, tagRanking): 
    if console['verboseLogging']: print "Getting parts of speech from generated chunks..."
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
        # todo: figure out toggles
        if "NP" in chunk:
            POSList.extend(["DT"] + [adverbChoice] + [adjectiveChoice] + [nounChoice] + ["PRP"])  # + ["PRP"] Toggle at end
        elif "PP" in chunk:
            POSList.extend(["TO", "IN"])
        elif "VP" in chunk:
            POSList.extend([adverbChoice] + ["MD"] + [verbChoice])  # [adverbChoice] + ["MD"] + [verbChoice]
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

def fill_simple_pos(POSList):
    #print POSList
    CClist = []
    DTlist = []
    INlist = []
    MDlist = []
    RPlist = []
    UHlist = []

    with connection:
        for partOfSpeech in ["CC", "DT", "IN", "MD", "RP", "UH"]:
            with connection:
                cursor.execute("SELECT word FROM dictionary WHERE part_of_speech = \"%s\"" % partOfSpeech)
                SQLReturn = cursor.fetchall()
            if partOfSpeech == "CC": CClist = SQLReturn
            elif partOfSpeech == "DT": DTlist = SQLReturn
            elif partOfSpeech == "IN": INlist = SQLReturn
            elif partOfSpeech == "MD": MDlist = SQLReturn
            elif partOfSpeech == "RP": RPlist = SQLReturn
            elif partOfSpeech == "UH": UHlist = SQLReturn

    reply = []
    for partOfSpeech in POSList:
        if partOfSpeech == "CC":
            if CClist: reply.append(random.choice(CClist)[0])
            else: reply.append(u"%")
        elif partOfSpeech == "DT":
            if CClist: reply.append(random.choice(DTlist)[0])
            else: reply.append(u"%")
        elif partOfSpeech == "IN":
            if CClist: reply.append(random.choice(INlist)[0])
            else: reply.append(u"%")
        elif partOfSpeech == "MD":
            if CClist: reply.append(random.choice(MDlist)[0])
            else: reply.append(u"%")
        elif partOfSpeech == "RP":
            if CClist: reply.append(random.choice(RPlist)[0])
            else: reply.append(u"%")
        elif partOfSpeech == "UH":
            if CClist: reply.append(random.choice(UHlist)[0])
            else: reply.append(u"%")
        elif partOfSpeech == "TO":
            reply.append(u"to")
        else:
            reply.append(partOfSpeech)
    #print reply
    return reply