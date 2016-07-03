# Name:             Sentence Generator
# Description:      Generates sentences based on what Emma knows about English and the world
# Section:          REPLY
import random
import re

import sqlite3 as sql
import pattern.en
from colorama import init, Fore
init(autoreset = True)

import utilities
from config import console, files

connection = sql.connect(files['dbPath'])
cursor = connection.cursor()

# Note: do not use greeting terms longer than 3 words
greetingTerms = [[u'what\'s', u'up'], [u'hi'], [u'hello'], [u'what', u'up'], [u'wassup'], [u'what', u'is', u'up'], [u'what\'s', u'going', u'on'], [u'how', u'are', u'you'], [u'howdy'], [u'hey']]

def generate_sentence(tokenizedMessage, asker=""):
    print "Creating reply..."
    print "Determining important words..."
    importantWords = []
    message = []
    for sentence in tokenizedMessage:
        for word in sentence:
            message.append(word[0])
            if word[1] in utilities.nounCodes and word[3] and word[0] not in importantWords:
                importantWords.append(word[0])

    primaryHalo, secondaryHalo = make_common_sense_halo(importantWords)

    '''
    reply = ['%']
    remainingIntents = [random.choice(intents) for _ in range(len(intents))]
    while '%' in reply:
        if remainingIntents == []: return ['%']
        reply = random.choice(remainingIntents)
        remainingIntents.remove(reply)
        domainsExpanded = False
        while not domainsExpanded:
            print reply
            newReply = expand_domains(importantWords, reply)
            if reply == newReply: domainsExpanded = True
            reply = newReply
    '''
    
    reply[-1] += u"."
    reply[0] = reply[0][0].upper + reply[0][1:]

    for greeting in greetingTerms:
        match = re.match(' '.join(greeting), ' '.join(message[0:3]))
        if match:
            reply = [random.choice([u"Hi", u"Hello"]) + u",", u"@" + asker, u"!"] + reply
            break

    # Fix positions of punctuation, refer to Alex and Ellie as mom and dad
    for count, word in enumerate(reply):
        if word in [u"sharkthemepark", u"sharkthemeparks", u"@sharkthemepark"]: reply[count] = u"mom"
        elif word in [u"nosiron", u"nosirons", u"@nosiron"]: reply[count] = u"dad"
        elif word in [u",", u"!", u"?"]:
            reply[count - 1] += word
            del reply[count]

    return ' '.join(reply)

def make_common_sense_halo(importantWords, depth=2):
    print "Creating common sense halo..."
    csHalo = importantWords
    for i in range(0, depth):
        foundWords = []
        for word in csHalo:
            with connection:
                cursor.execute("SELECT target FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.target = dictionary.word WHERE associationmodel.word = \'%s\' AND part_of_speech IN (\'NN\', \'NNS\', \'NNP\', \'NNPS\');" % word)
                SQLReturn = cursor.fetchall()
            for fetchedWord in SQLReturn:
                if fetchedWord[0] not in csHalo: foundWords.extend(fetchedWord)
        csHalo.extend(foundWords)

    for word in csHalo:
        if word in importantWords: csHalo.remove(word)

    return csHalo

def get_associations(importantWords, csHalo):
    print "Finding associations..."
    for word in importantWords:
        with connection:
            cursor.execute("SELECT * FROM associationmodel WHERE word = \'%s\';" % word)
            primaryAssociations = cursor.fetchall()
    for word in csHalo:
        with connection:
            cursor.execute("SELECT * FROM associationmodel WHERE word = \'%s\';" % word)
            secondaryAssociations = cursor.fetchall()
    return primaryAssociations, secondaryAssociations

def choose_association(associations):
    dieSeed = 0
    for row in associations: dieSeed += row[3]
    dieResult = random.uniform(0, dieSeed)
    for row in associations:
        dieResult -= row[3]
        if dieResult <= 0:
            return row
            break

# Define intents
intents = ['COMPARATIVE', 'DECLARATIVE', 'IMPERATIVE', 'PHRASE']        # Greeting and Interrogative intents are special

greetingDomains = []
comparativeDomains = []
declarativeDomains = []
imperativeDomains = []
interrogativeDomains = []
phraseDomains = []

allowGreeting = False
allowComparative = False
allowDeclarative = False
allowImperative = False
allowInterrogative = False
allowPhrase = False

def makeGreeting():
    pass

def makeComparative():
    pass

def makeDeclarative():
    pass

def makeImperative():
    pass

def makeInterrogative():
    pass

def makePhrase():
    pass