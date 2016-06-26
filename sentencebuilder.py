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

intents = [['=DECLARATIVE'], ['=DECLARATIVE', 'like', '=DECLARATIVE'], ['=DECLARATIVE', 'and', '=DECLARATIVE'], ['=DECLARATIVE', ',', 'but', '=DECLARATIVE'], ['=IMPERATIVE'], ['=IMPERATIVE', 'like', '=DECLARATIVE'], ['=PHRASE']]

declaratives = [['=PHRASE', 'is', '=ADJECTIVE'], ['=PLURPHRASE', 'are', '=ADJECTIVE'], ['=PHRASE', '=IMPERATIVE']]
imperatives = [['=VERB'], ['=VERB', '=PHRASE'], ['=VERB', 'me'], ['=VERB', '(a/an)', '=PHRASE'], ['=VERB', 'the', '=PLURPHRASE'], ['=VERB', 'the', '=PHRASE', '=ADVERB'], ['=VERB', 'at', '=PLURPHRASE'], ['=VERB', '(a/an)', '=PHRASE', 'with', '=PLURPHRASE'], ['always', '=VERB', '=PHRASE'], ['never', '=VERB', '=PHRASE']]
phrases =[['=NOUN'], ['=ADJECTIVE', '=NOUN'], ['=ADJECTIVE', ',', '=ADJECTIVE', '=NOUN']]
greetings = [['hi', '=NAME', '!'], ['hello', '=NAME', '!'], ['what\'s', 'up,', '=NAME', '?']]
def create_reply(importantWords, associations):

    reply = random.choice(intents)
    domainsExpanded = False

    while not domainsExpanded:
        print reply
        newReply = expand_domains(reply)
        if reply == newReply: domainsExpanded = True
        reply = newReply

    return reply

def expand_domains(reply):
    newReply = []
    for word in reply:
        if word == "=DECLARATIVE":
            newReply.append(random.choice(declaratives))
        elif word == "=IMPERATIVE":
            newReply.append(random.choice(imperatives))
        elif word in ["=PHRASE", "=PLURPHRASE"]:
            newReply.append(random.choice(phrases))
        elif type(word) == list:
            newReply.append(expand_domains(word))
        else: newReply.append(word)
    return newReply

create_reply([u'sharkthemepark', u'dog'], [[u'pure', u'IS-PROPERTY-OF', u'sharkthemepark', 0.0999999999997], [u'sharkthemepark', u'HAS-ABILITY-TO', u'love', 0.0999999999997], [u'dog', u'HAS-ABILITY-TO', u'pass', 0.0999999999997], [u'gay', u'IS-PROPERTY-OF', u'dog', 0.450853060378], [u'dominant', u'IS-PROPERTY-OF', u'dog', 0.0999999999997], [u'siberian', u'IS-PROPERTY-OF', u'dog', 0.0999999999997], [u'dog', u'HAS-ABILITY-TO', u'gonna', 0.0999999999997], [u'pure', u'IS-PROPERTY-OF', u'joy', 0.0999999999997], [u'pure', u'IS-PROPERTY-OF', u'sharkthemepark', 0.0999999999997]])