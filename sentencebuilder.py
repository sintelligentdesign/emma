# -*- coding: utf-8 -*-

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
    importantWords = []
    for sentence in tokenizedMessage:
        for word in sentence:
            if word[1] in utilities.nounCodes and word[3]:
                importantWords.append(word[0])
    if console['verboseLogging']: print Fore.BLUE + u"Important words: " + str(importantWords)

    # find words related to the important words
    depth1 = []
    depth2 = []
    associations = []
    for word in importantWords:
        depth1.extend(find_associations(word))
    for word in depth1:
        depth2.extend(find_associations(word[0]))
        associations.append(word)
    for word in depth2:
        associations.append(word)
    if console['verboseLogging']: print Fore.BLUE+ u"Associations: " + str(associations)

    # Reply to message
    print "Creating reply..."
    reply = create_reply(importantWords, associations)
    return reply, importantWords, associations

def find_associations(word):
    associations = []
    with connection:
        cursor.execute("SELECT word, association_type, target, weight FROM associationmodel WHERE word = \"%s\" OR target = \"%s\";" % (word.encode('utf-8'), word.encode('utf-8')))
        SQLReturn = cursor.fetchall()
    for row in SQLReturn:
        relatedWord = [row[0], row[1], row[2], row[3]]
        associations.append(relatedWord)
    # todo: remove duplicates
    if console['verboseLogging']: print Fore.MAGENTA + u"Found %d associations for %s" % (len(associations), word)
    return associations

def create_reply(importantWords, associations):
    reply = []
    verbAssociations = []
    chosenVerb = ''
    for row in associations:
        with connection:
            cursor.execute("SELECT * FROM dictionary WHERE word = \'%s\' AND part_of_speech IN (\'VB\', \'VBD\', \'VBG\', \'VBN\', \'VBP\', \'VBZ\');" % row[2])
            SQLReturn = cursor.fetchall()
            if SQLReturn:
                verbAssociations.extend(row)
    verbsWithWeights = []
    for count in range(0 ,len(verbAssociations) / 4):
        verbWeightTuple = (verbAssociations[(4 * count) - 2], verbAssociations[(4 * count) - 1])
        verbsWithWeights.append(verbWeightTuple)
    dieSeed = 0
    for verbWeightTuple in verbsWithWeights:
        dieSeed += verbWeightTuple[1]
    dieResult = random.uniform(0, dieSeed)
    for verbWeightTuple in verbsWithWeights:
        dieResult -= verbWeightTuple[1]
        if dieResult <= 0:
            chosenVerb = verbWeightTuple[0]
            break

    return chosenVerb

print create_reply([u'sharkthemepark', u'dog'], [[u'pure', u'IS-PROPERTY-OF', u'sharkthemepark', 0.0999999999997], [u'sharkthemepark', u'HAS-ABILITY-TO', u'love', 0.0999999999997], [u'dog', u'HAS-ABILITY-TO', u'pass', 0.0999999999997], [u'gay', u'IS-PROPERTY-OF', u'dog', 0.450853060378], [u'dominant', u'IS-PROPERTY-OF', u'dog', 0.0999999999997], [u'siberian', u'IS-PROPERTY-OF', u'dog', 0.0999999999997], [u'dog', u'HAS-ABILITY-TO', u'gonna', 0.0999999999997], [u'pure', u'IS-PROPERTY-OF', u'joy', 0.0999999999997], [u'pure', u'IS-PROPERTY-OF', u'sharkthemepark', 0.0999999999997]])
