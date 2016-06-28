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

connection = sql.connect(database["path"])
cursor = connection.cursor()

def generate_sentence(tokenizedMessage):
    importantWords = []
    for sentence in tokenizedMessage:
        for word in sentence:
            if word[1] in utilities.nounCodes and word[3] and word[0] not in importantWords:
                importantWords.append(word[0])
    if console['verboseLogging']: print Fore.BLUE + u"Important words: " + str(importantWords)

    # Reply to message
    print "Creating reply..."
    reply = ' '.join(create_reply(importantWords))
    return reply

def choose_association(associations):
    dieSeed = 0
    for row in associations: dieSeed += row[3]
    dieResult = random.uniform(0, dieSeed)
    for row in associations:
        dieResult -= row[3]
        if dieResult <= 0:
            return row
            break

intents = [['=DECLARATIVE'], ['=DECLARATIVE', 'like', '=DECLARATIVE'], ['=DECLARATIVE', 'and', '=DECLARATIVE'], ['=DECLARATIVE', ',', 'but', '=DECLARATIVE'], ['=IMPERATIVE'], ['=IMPERATIVE', 'like', '=DECLARATIVE']]

declaratives = [['=PHRASE', 'is', '=ADJECTIVE'], ['=PLURPHRASE', 'are', '=ADJECTIVE'], ['=PHRASE', '=IMPERATIVE']] #['=PHRASE', 'has/have', '=PHRASE']  todo: this would be a special case. Should we have a few special case domains that get their own special code?
imperatives = [['=VERB', '=PHRASE'], ['=VERB', 'a', '=PHRASE'], ['=VERB', 'the', '=PHRASE'], ['=VERB', 'the', '=PLURPHRASE'], ['=VERB', 'at', '=PLURPHRASE'], ['always', '=VERB', '=PHRASE'], ['never', '=VERB', '=PHRASE']] #['=VERB', 'a', '=PHRASE', 'with', '=PLURPHRASE']
phrases =[['=NOUN'], ['=ADJECTIVE', '=NOUN'], ['=ADJECTIVE', ',', '=ADJECTIVE', '=NOUN']]
greetings = [['hi', '=NAME', '!'], ['hello', '=NAME', '!'], ['what\'s', 'up,', '=NAME', '?']]


def create_reply(importantWords):
    reply = ['%']
    remainingIntents = intents
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

    reply[-1] += u"."
    reply[0] = reply[0].title()
    for count, word in enumerate(reply):
        # having to fix the position of commas ANYWAY gives us the ability to throw in a cute little easter egg when referencing Alex or Ellie's Tumblr usernames
        if word == "sharkthemepark":
            reply[count] = "mom"
        elif word == "nosiron":
            reply[count] = "dad"
        elif word == ",":
            reply[count - 1] = reply[count - 1] + u","
            del reply[count]
    return reply

def expand_domains(importantWords, reply):
    newReply = []
    for count, word in enumerate(reply):
        if word == "=DECLARATIVE":
            newReply.extend(build_declarative(importantWords))
            print newReply + reply[count + 1:len(reply)]
        elif word == "=IMPERATIVE":
            newReply.extend(build_imperative(importantWords))
            print newReply + reply[count + 1:len(reply)]
        elif word in ["=PHRASE", "=PLURPHRASE"]:
            if word == "=PHRASE":
                newReply.extend(build_phrase(importantWords, False))
            elif word == "=PLURPHRASE":
                newReply.extend(build_phrase(importantWords, True))
            print newReply + reply[count + 1:len(reply)]
        elif type(word) == list:
            newReply.append(expand_domains(importantWords, word))
        else:
            newReply.append(word)
    return newReply

def build_phrase(importantWords, isPlural, returnSet=False):
    queriedWords = []
    queriedWords.extend(importantWords)
    for word in importantWords:
        with connection:
            cursor.execute("SELECT target FROM associationmodel WHERE word = \"%s\" AND association_type in (\"IS-A\", \"HAS\");" % word)
            SQLReturn = (cursor.fetchall())
        for word in SQLReturn: queriedWords.extend(word)

    phraseSets = []
    for word in queriedWords:
        with connection:
            cursor.execute("SELECT * FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.word = dictionary.word WHERE target = \"%s\" AND association_type = \"IS-PROPERTY-OF\" AND part_of_speech IN (\"JJ\", \"JJR\", \"JJS\");" % word)
            SQLReturn = cursor.fetchall()
        if SQLReturn != []: phraseSets.append([word, choose_association(SQLReturn)[0], choose_association(SQLReturn)[0]])

    # todo: handle errors correctly lmao
    if phraseSets == []: return ["%", "%"]

    phrase = []
    domain = random.choice(phrases)
    phraseSet = random.choice(phraseSets)
    for word in domain:
        if word == "=NOUN":
            if isPlural: phrase.append(pattern.en.pluralize(phraseSet[0]))
            else: phrase.append(phraseSet[0])
        elif word == "=ADJECTIVE":
            phrase.append(phraseSet[1])
            del phraseSet[1]
        else: phrase.append(word)
    if returnSet: return phrase, phraseSet
    else: return phrase

def build_imperative(importantWords):
    domain = random.choice(imperatives)
    pluralPhrase = True if "=PLURPHRASE" in domain else False
    phrase, phraseSet = build_phrase(importantWords, pluralPhrase, True)
    if phrase == "%": return "%"

    # Using the noun from our phrase, find matching verbs and adverbs
    with connection:
        cursor.execute("SELECT * FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.word = dictionary.word WHERE target = \"%s\" AND association_type IN (\"IS-PROPERTY-OF\", \"IS-OBJECT-OF\") AND part_of_speech IN (\'VB\', \'VBD\', \'VBG\', \'VBN\', \'VBP\', \'VBZ\', \'RB\', \'RBR\', \'RBS\', \'RP\');" % phraseSet[0])
        verbAssociations = cursor.fetchall()

    if verbAssociations == []: return "%"

    verb = choose_association(verbAssociations)[0]

    imperative = []
    for word in domain:
        if word in ["=PHRASE", "=PLURPHRASE"]: imperative.extend(phrase)
        elif word == "=VERB": imperative.append(verb)
        else: imperative.append(word)
    return imperative

def build_declarative(importantWords):
    domain = random.choice(declaratives)
    pluralPhrase = True if "=PLURPHRASE" in domain else False
    phrase, phraseSet = build_phrase(importantWords, pluralPhrase, True)
    if phrase == "%": return "%"
    imperative = build_imperative([phraseSet[0]])

    with connection:
        cursor.execute("SELECT * FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.word = dictionary.word WHERE target = \"%s\" AND association_type = \"IS-PROPERTY-OF\" AND part_of_speech IN (\"JJ\", \"JJR\", \"JJS\");" % phraseSet[0])
        adjectiveAssociations = cursor.fetchall()

    adjective = choose_association(adjectiveAssociations)[0]

    declarative = []
    for word in domain:
        if word in ["=PHRASE", "=PLURPHRASE"]: declarative.extend(phrase)
        elif word == "=IMPERATIVE": declarative.extend(imperative)
        elif word == "=ADJECTIVE": declarative.append(adjective)
        else: declarative.append(word)
        return declarative