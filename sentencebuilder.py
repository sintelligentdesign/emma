# -*- coding: utf-8 -*-

# Name:             Sentence Generator
# Description:      Generates sentences based on what Emma knows about English and the world
# Section:          REPLY
import random

import sqlite3 as sql
import pattern.en
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

    if console['verboseLogging']: print Fore.BLUE+ u"Associations: " + str(associations)

    # Reply to message
    print "Creating reply..."
    reply = create_reply(importantWords)
    return reply, importantWords

def common_sense_halo(importantWords):
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

# Reply > Intent > Domain > Parts of Speech
intents = [['=DECLARATIVE'], ['=DECLARATIVE', 'like', '=DECLARATIVE'], ['=DECLARATIVE', 'and', '=DECLARATIVE'], ['=DECLARATIVE', ',', 'but', '=DECLARATIVE'], ['=IMPERATIVE'], ['=IMPERATIVE', 'like', '=DECLARATIVE'], ['=PHRASE']]

declaratives = [['=PHRASE', 'is', '=ADJECTIVE'], ['=PLURPHRASE', 'are', '=ADJECTIVE'], ['=PHRASE', '=IMPERATIVE']]
imperatives = [['=VERB'], ['=VERB', '=PHRASE'], ['=VERB', '(a/an)', '=PHRASE'], ['=VERB', 'the', '=PHRASE'], ['=VERB', 'the', '=PLURPHRASE'], ['=VERB', 'at', '=PLURPHRASE'], ['always', '=VERB', '=PHRASE'], ['never', '=VERB', '=PHRASE']] #['=VERB', '(a/an)', '=PHRASE', 'with', '=PLURPHRASE']
phrases =[['=NOUN'], ['=ADJECTIVE', '=NOUN'], ['=ADJECTIVE', ',', '=ADJECTIVE', '=NOUN']]
greetings = [['hi', '=NAME', '!'], ['hello', '=NAME', '!'], ['what\'s', 'up,', '=NAME', '?']]
def create_reply(importantWords):
    reply = random.choice(intents)
    domainsExpanded = False
    while not domainsExpanded:
        print reply
        newReply = expand_domains(importantWords, reply)
        if reply == newReply: domainsExpanded = True
        reply = newReply
    return reply

def expand_domains(importantWords, reply):
    newReply = []
    for word in reply:
        if word == "=DECLARATIVE":
            newReply.append(random.choice(declaratives))
        elif word == "=IMPERATIVE":
            newReply.extend(build_imperative(importantWords))
        elif word in ["=PHRASE", "=PLURPHRASE"]:
            if word == "=PHRASE":
                newReply.extend(build_phrase(importantWords, False))
            elif word == "=PLURPHRASE":
                newReply.extend(build_phrase(importantWords, True))
        elif type(word) == list:
            newReply.append(expand_domains(importantWords, word))
        else: newReply.append(word)
    return newReply

def build_phrase(importantWords, isPlural, returnSet=False):
    queriedWords = []
    queriedWords.extend(importantWords)
    for word in importantWords:
        with connection:
            cursor.execute("SELECT target FROM associationmodel WHERE word = \'%s\' AND association_type = \'HAS\';" % word)
            SQLReturn = (cursor.fetchall())
        for word in SQLReturn: queriedWords.extend(word)
            
    phraseSets = []
    for word in queriedWords:
        with connection:
            cursor.execute("SELECT * FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.word = dictionary.word WHERE target = \'%s\' AND association_type = \'IS-PROPERTY-OF\' AND part_of_speech = \'JJ\';" % word)
            SQLReturn = cursor.fetchall()
        if SQLReturn != []: phraseSets.append([word, choose_association(SQLReturn)[0], choose_association(SQLReturn)[0]])

    phrase = []
    domain = random.choice(phrases)
    phraseSet = random.choice(phraseSets)
    for word in domain:
        if word == "=NOUN": 
            if isPlural:
                phrase.append(pattern.en.pluralize(phraseSet[0]))
            else: phrase.append(phraseSet[0])
        elif word == "=ADJECTIVE":
            phrase.append(phraseSet[1])
            del phraseSet[1]
        else: phrase.append(word)
    if returnSet: return phrase, phraseSet
    else: return phrase

def build_imperative(importantWords):
    domain = random.choice(imperatives)
    pluralPhrase = False
    if "=PLURPHRASE" in domain: pluralPhrase = True
    phrase, phraseSet = build_phrase(importantWords, pluralPhrase, True)

    # Using the noun from our phrase, find matching verbs and adverbs
    with connection:
        cursor.execute("SELECT * FROM associationmodel WHERE target = \'%s\' AND association_type = \'IS-PROPERTY-OF\';" % phraseSet[0])
        verbAssociations = cursor.fetchall()

    verb = choose_association(verbAssociations)[0]

    imperative = []
    print domain
    for word in domain:
        if word in ["=PHRASE", "=PLURPHRASE"]: imperative.append(phrase)
        elif word == "=VERB": imperative.append(verb)
        else: imperative.append(word)
    return imperative

#create_reply([u'affection', u'dog'])
print build_imperative([u'affection', u'dog'], True)