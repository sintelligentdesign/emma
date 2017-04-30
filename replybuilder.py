import logging
import random
import re

import sqlite3 as sql

connection = sql.connect('emma.db')
cursor = connection.cursor()

class Sentence:
    def __init__(self):
        self.domain = str
        self.topic = str

class Chunk:
    def __init__(self):
        pass

class SBBHaveHas:
    def __init__(self):
        pass

class SBBIsAre:
    def __init__(self):
        pass

class Association:
    def __init__(self, word, associationType, target, weight):
        self.word = word
        self.target = target
        self.associationType = associationType
        self.weight = weight

def weighted_roll(choices):
    """Takes a list of (weight, option) tuples and makes a weighted die roll"""
    dieSeed = 0
    for choice in choices:
        dieSeed += choice[0]
    dieResult = random.uniform(0, dieSeed)

    for choice in choices:
        dieResult -= choice[0]
        if dieResult <= 0:
            return choice[1]

def find_associations(keyword):
    """Finds associations in our association model for given keywords"""
    logging.debug("Finding associations for {0}...".format(keyword)) 
    associations = []
    with connection:
        cursor.execute('SELECT * FROM associationmodel WHERE word = \"{0}\" OR target = \"{1}\";'.format(keyword, keyword))
        SQLReturn = cursor.fetchall()
        for row in SQLReturn:
            associations.append(Association(row[0], row[1], row[2], row[3]))
    return associations

def reply(message):
    """Replies to a Message object using the associations we built using train()"""
    logging.info("Building reply...")
    reply = []

    # Make sure we can actually generate a reply
    if len(message.keywords) > 0:
        pass
    else:
        raise IndexError('No keywords in Message object. Sentence generation failed.')

    # Decide how many sentences long our reply will be (excluding greetings, which don't count because a message could be just a greeting)
    minSentences = 1
    maxSentences = 4
    sentences = random.randint(minSentences, maxSentences)
    for i in range(0, sentences):
        reply.append(Sentence())
    logging.debug("Generating {0} sentences...".format(sentences))

    # Choose the sentences' topics and domains
    logging.info("Choosing sentence topics and domains...")
    logging.debug("Message has {0} keywords".format(len(message.keywords)))
    logging.debug("Keywords: {0}".format(str(message.keywords)))
    for i, sentence in enumerate(reply):
        logging.debug("Choosing topic for sentence {0}...".format(i))
        sentence.topic = weighted_roll(message.keywords)

        # Look up associations for the keyword
        logging.debug("Choosing domain for sentence {0}...".format(i))
        associations = find_associations(sentence.topic)

        # Choose a domain based on the associations
        # Decide what domains are valid to be chosen
        canBeDeclarative = False
        canBeImperative = False
        for association in associations:
            if association.associationType == 'HAS' or association.associationType == "IS-A" or association.associationType == "HAS-ABILITY-TO":
                canBeDeclarative = True
            if association.associationType == "HAS-ABILITY-TO":
                canBeImperative = True

        # Choose a domain from the set of valid domains
        domains = ['phrase', 'interrogative']
        if canBeDeclarative:
            domains.append('declarative')
        if canBeImperative:
            domains.append('imperative')

        sentence.domain = random.choice(domains)
        logging.debug("Chose {0}".format(sentence.domain))

    # Domains:
    #   Declarative
    #   Imperative
    #   Interrogative
    #   Phrase
    #   Greeting

    return reply