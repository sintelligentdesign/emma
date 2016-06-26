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
            if word[1] in utilities.nounCodes and word[3] and word[0] not in importantWords:
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

def choose_association(associations):
    dieSeed = 0
    for row in associations: dieSeed += row[3]
    dieResult = random.uniform(0, dieSeed)
    for row in associations:
        dieResult -= row[3]
        if dieResult <= 0:
            return row
            break

def create_reply(importantWords, associations):
    reply = ""
    verbAssociations = []
    for row in associations:
        with connection:
            cursor.execute("SELECT * FROM dictionary WHERE word = \"%s\" AND part_of_speech IN (\'VB\', \'VBD\', \'VBG\', \'VBN\', \'VBP\', \'VBZ\');" % row[2])
            SQLReturn = cursor.fetchall()
            if SQLReturn: verbAssociations.append(row)

    # Choose a verb to seed our sentence
    verbChoice = choose_association(verbAssociations)
    print u"verbChoice:" + str(verbChoice)
            
    with connection:
        importantWordsSQL = u"("
        for count, word in enumerate(importantWords):
            importantWordsSQL += u"\"" + word + u"\""
            if count != len(importantWords) - 1:
                importantWordsSQL += u","
        importantWordsSQL += u")"
        cursor.execute("SELECT * FROM associationmodel WHERE word IN %s AND association_type = \"HAS-ABILITY-TO\" AND target = \"%s\";" % (importantWordsSQL, verbChoice[2]))
        sbjAssociations = cursor.fetchall()
        if sbjAssociations == []:
            cursor.execute("SELECT * FROM associationmodel WHERE association_type = \"HAS-ABILITY-TO\" AND target = \"%s\";" % verbChoice[2])
            sbjAssociations = cursor.fetchall()

    # Choose a subject noun
    sbjChoice = choose_association(sbjAssociations)
    print u"sbjChoice:" + str(sbjChoice)

    reply = sbjChoice[0] + u" " + verbChoice[2]

    return reply