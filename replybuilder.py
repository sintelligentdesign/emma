import logging
import random
import re

import sqlite3 as sql

import misc

connection = sql.connect('emma.db')
cursor = connection.cursor()

class SBBWord:
    def __init__(self, word, partOfSpeech):
        self.word = word
        self.partOfSpeech = str

        with connection:
            cursor.execute('SELECT part_of_speech FROM dictionary WHERE word = \"{0}\";'.format(self.word))
            SQLReturn = cursor.fetchall()
            self.partOfSpeech = SQLReturn[0]
            
class Sentence:
    def __init__(self):
        self.domain = str
        self.topic = str
        # TODO: stuff with plurality
        #self.plurality = False
        self.contents = ['something']

class SBBHaveHas:
    def __init__(self):
        pass

class SBBIsAre:
    def __init__(self):
        pass

class SBBArticle:
    def __init__(self):
        pass

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

def find_part_of_speech(keyword):
    """Looks in our dictionary for the part of speech of a given keyword"""
    # TODO: Make this able to handle words with more than one usage
    logging.debug("Looking up \"{0}\" in the dictionary...".format(keyword))
    with connection:
        cursor.execute('SELECT part_of_speech FROM dictionary WHERE word = \"{0}\";'.format(keyword))
        SQLReturn = cursor.fetchall()
        if SQLReturn:
            return SQLReturn[0]
        else:
            return "NN"

# TODO: Random choices should be influenced by mood or other
def make_declarative(topic):
    pass

def make_imperative(topic):
    pass

def make_interrogative(topic):
    pass

def make_simple(topic, sentence):
    # Look for adjectives to describe the object
    associations = find_associations(topic)

    # Decide whether to add an article
    if random.choice([True, False]):
            sentence.contents += SBBArticle()

    # Decide whether to add an adjective, and how many
    for i in range(random.randint(1, 2)):
        adjectiveAssociations = []
        for association in associations:
            if association.associationType == "HAS-PROPERTY" and association.word == topic:
                adjectiveAssociations.append((association.weight, association))
        if len(adjectiveAssociations) > 0:
            if random.choice([True, False]):
                sentence.contents.append(association.target)

    # Add the word
    print sentence
    sentence.contents += topic

    return sentence
        
def make_compound(topic1, topic2):
    pass

def make_greeting():
    pass

class Association:
    def __init__(self, word, associationType, target, weight):
        self.word = word
        self.target = target
        self.associationType = associationType
        self.weight = weight
        
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
        sentence.topic = random.choice(message.keywords)

        # Look up associations for the keyword
        logging.debug("Choosing domain for sentence {0}...".format(i))
        associations = find_associations(sentence.topic)

        # Choose a domain based on the associations
        # Decide what domains are valid to be chosen
        # Interrogative is always valid, so the list starts with it prepopulated
        domains = ['interrogative']
        canBeDeclarative = False
        canBeImperative = False
        for association in associations:
            if association.associationType == 'HAS' or association.associationType == "IS-A" or association.associationType == "HAS-ABILITY-TO":
                canBeDeclarative = True
            if association.associationType == "HAS-ABILITY-TO":
                canBeImperative = True
        if canBeDeclarative:
            domains.append('declarative')
        if canBeImperative:
            domains.append('imperative')
        if find_part_of_speech(sentence.topic) in misc.nounCodes:
            domains.append('simple')
            if len(associations) > 1:
                domains.append('compound')

        #sentence.domain = random.choice(domains)
        sentence.domain = 'simple'
        logging.debug("Chose {0}".format(sentence.domain))

        # Build sentence structures
        logging.info("Building sentence structures...")
        for i, sentence in enumerate(reply):
            if sentence.domain == 'declarative':
                sentence.contents = make_declarative(sentence.topic)
            elif sentence.domain == 'imperative':
                sentence.contents = make_imperative(sentence.topic)
            elif sentence.domain == 'interrogative':
                sentence.contents = make_interrogative(sentence.topic)
            elif sentence.domain == 'simple':
                sentence.contents = make_simple(sentence.topic, sentence)
            elif sentence.domain == 'compound':
                sentence.contents = make_compound(sentence.topic)

        print sentence.contents
    return reply