import logging
import random
import re
import string

import sqlite3 as sql

import misc

connection = sql.connect('emma.db')
cursor = connection.cursor()

class Sentence:
    def __init__(self):
        self.domain = ''
        self.topic = ''
        self.isPlural = False
        self.contents = []

class SBBWord:
    def __init__(self, word, partOfSpeech):
        self.word = word
        self.partOfSpeech = str

        with connection:
            cursor.execute('SELECT part_of_speech FROM dictionary WHERE word = \"{0}\";'.format(self.word))
            SQLReturn = cursor.fetchall()
            self.partOfSpeech = SQLReturn[0]

class SBBHaveHas:
    def __init__(self):
        pass

class SBBIsAre:
    def __init__(self):
        pass

class SBBArticle:
    def __init__(self):
        pass

class SBBConjunction:
    def __init__(self):
        pass

class SBBPunctuation:
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

class Association:
    def __init__(self, word, associationType, target, weight):
        self.word = word
        self.target = target
        self.associationType = associationType
        self.weight = weight

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
def make_declarative(sentence):
    # Look for HAS, IS-A or HAS-ABILITY-TO associations 
    associations = find_associations(sentence.topic)
    hasAssociations = []
    isaAssociations = []
    hasabilitytoAssociations = []
    haspropertyAssociations = []
    for association in associations:
        if association.associationType == "HAS" and association.word == sentence.topic:
            hasAssociations.append((association.weight, association))
        elif association.associationType == "IS-A" and association.word == sentence.topic:
            isaAssociations.append((association.weight, association))
        elif association.associationType == "HAS-ABILITY-TO" and association.word == sentence.topic:
            hasabilitytoAssociations.append((association.weight, association))
        elif association.associationType == "HAS-PROPERTY" and association.word == sentence.topic:
            haspropertyAssociations.append((association.weight, association))
            
    # If we have associations other than HAS-PROPERTY ones, we can make more complex sentences
    allowComplexDeclarative = False
    if len(hasAssociations) > 0 or len(isaAssociations) or len(hasabilitytoAssociations) > 0:
        allowComplexDeclarative = True

    # Decide what kind of sentence to make and make it
    if random.choice([False, allowComplexDeclarative]):
        # Complex
        # Decide /what kinds/ of complex sentence we can make
        validSentenceAspects = []
        if len(hasAssociations) > 0:
            validSentenceAspects.append('HAS')
        if len(isaAssociations) > 0:
            validSentenceAspects.append('IS-A')
        if len(hasabilitytoAssociations) > 0:
            validSentenceAspects.append('HAS-ABILITY-TO')
        # Choose the kind of sentence to make
        sentenceAspect = random.choice(validSentenceAspects)

        sentence.contents.append(sentence.topic)

        if sentenceAspect == 'HAS':
            sentence = make_simple(sentence)
            sentence.contents.append(SBBHaveHas())
            sentence.contents.append(weighted_roll(hasAssociations).target)
        elif sentenceAspect == 'IS-A':
            sentence = make_simple(sentence)
            sentence.contents.extend([u'is', SBBArticle])
            sentence.contents.append(weighted_roll(isaAssociations).target)
        elif sentenceAspect == 'HAS-ABILITY-TO':
            sentence = make_simple(sentence)
            sentence.contents.append(u'can')
            sentence.contents.append(weighted_roll(hasabilitytoAssociations).target)
    else:
        # Simple
        if random.choice([True, False]):
            sentence = make_simple(sentence)
        else:
            sentence.contents.append(sentence.topic)
        sentence.contents.append(u'is')
        sentence.contents.append(weighted_roll(haspropertyAssociations).target)
        
    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_imperative(sentence):
    # Coin Flip to decide whether to add always or never
    if random.choice([True, False]):
        sentence.contents.append(random.choice([u'always', u'never']))

    # Look for things the object can do
    associations = find_associations(sentence.topic)

    # Get HAS-ABILITY-TO associations and also look for HAS associations
    hasabilitytoAssociations = []
    hasAssociations = []
    for association in associations:
        if association.associationType == "HAS-ABILITY-TO" and association.word == sentence.topic:
            hasabilitytoAssociations.append((association.weight, association))
        elif association.associationType == "HAS" and association.word == sentence.topic:
            hasAssociations.append((association.weight, association))

    # If we have HAS associations, we can make slightly more complex sentences
    allowComplexImperative = False
    if len(hasAssociations) > 0:
        allowComplexImperative = True

    # Choose what type of sentence to make
    if random.choice([False, allowComplexImperative]):
        # Complex
        sentence.contents.append(sentence.topic)
        sentence.contents.append(u'can')
        sentence.contents.append(weighted_roll(hasabilitytoAssociations).target)
        sentence.contents.extend([u'with', u'a'])
        sentence.contents.append(weighted_roll(hasAssociations).target)
    else:
        # Simple
        sentence.contents.append(weighted_roll(hasabilitytoAssociations).target)
        sentence.contents.append(SBBArticle())
        sentence.contents.append(sentence.topic)
        
    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_interrogative(sentence):
    # Start the setence with a template
    starters = [
        [u'what', u'is'],
        [u'what\'s'],
    ]
    sentence.contents.extend(random.choice(starters))

    # Add on the subject
    sentence = make_simple(sentence)

    sentence.contents.append(u'?')
    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_simple(sentence):
    # Look for adjectives to describe the object
    associations = find_associations(sentence.topic)

    # Decide whether to add an article
    if random.choice([True, False]):
        sentence.contents.append(SBBArticle())

    # See if we have any adjective associations handy
    haspropertyAssociations = []
    for association in associations:
        if association.associationType == "HAS-PROPERTY" and association.word == sentence.topic:
            haspropertyAssociations.append((association.weight, association))

    # If we do, put them all in a list and have a chance to add some to the sentence
    if len(haspropertyAssociations) > 0:
        # Add adjective(s)
        if len(haspropertyAssociations) > 1:
            for i in range(random.randint(0, 2)):
                sentence.contents.append(weighted_roll(haspropertyAssociations).target)
        else:
            sentence.contents.append(weighted_roll(haspropertyAssociations).target)
        # Add the word
        sentence.contents.append(sentence.topic)
        """
        # Alternate template that might live in make_declarative() later
        # Add the word
        sentence.contents.append(sentence.topic)
        # Add is/are
        sentence.contents.append(SBBIsAre)
        # Add an adjective
        sentence.contents.append(weighted_roll(haspropertyAssociations).target)
        # We can go one step further
        if random.choice([True, False]) and len(haspropertyAssociations) > 1:
            sentence.contents.append(u'and')
            sentence.contents.append(weighted_roll(haspropertyAssociations).target)
        """
    else:
        # If we have no adjectives, just add the word
        sentence.contents.append(sentence.topic)

    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence
        
def make_compound(sentence, altTopic):
    # This function gets an extra topic so that it can seed a second call of make_simple()
    # Make the first half of the sentence
    sentence = make_simple(sentence)

    # Make a 'fake' sentence to generate the second half of the sentence
    shellSentence = Sentence()
    shellSentence.topic = altTopic
    shellSentence.domain = 'simple'
    shellSentence = make_simple(shellSentence)

    # Have a chance to add a comma
    if random.choice([True, False]):
        sentence.contents[-1] = sentence.contents[-1] + u','

    # Add a conjunction to the end of the first sentence
    sentence.contents.append(SBBConjunction())

    # Paste the second half of the sentence onto the first half
    sentence.contents.extend(shellSentence.contents)

    logging.debug("Reply (in progress): {0}".format(str(sentence.contents)))
    return sentence

def make_greeting(message):
    # This function is a little different from the others, but it works pretty similarly
    # First we make a shell sentence, like in make_compound()
    shellSentence = Sentence()
    shellSentence.domain = 'greeting'

    # Start our sentence with a greeting
    starters = [
        [u'hi'],
        [u'hello'],
        [u'hey']
    ]
    shellSentence.contents.extend(random.choice(starters))

    # Coin flip for adding the word 'there'
    if random.choice([True, False]):
        shellSentence.contents.append(u'there')

    # Coin flip for adding a comma
    if random.choice([True, False]):
        shellSentence.contents[-1] = shellSentence.contents[-1] + u','

    # Add the message sender's username
    shellSentence.contents.append(message.sender)
    shellSentence.contents.append(SBBPunctuation())
    return shellSentence
        
def reply(message, moodValue):
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
        logging.debug("Choosing topic for sentence {0}...".format(i+1))
        sentence.topic = random.choice(message.keywords)

        # Look up associations for the keyword
        logging.debug("Choosing domain for sentence {0}...".format(i+1))
        associations = find_associations(sentence.topic)

        # Choose a domain based on the associations
        # Decide what domains are valid to be chosen
        validDomains = {
            'declarative': False,
            'imperative': False,
            'interrogative': False,
            'simple': False,
            'compound': False
        }
        for association in associations:
            if association.word == sentence.topic:
                if association.associationType == 'HAS-PROPERTY':
                    validDomains['declarative'] = True
                if association.associationType == "HAS-ABILITY-TO":
                    validDomains['imperative'] = True
                if association.associationType == "HAS-PROPERTY":
                    validDomains['simple'] = True
        if validDomains['simple'] and len(associations) > 1:
            validDomains['compound'] = True
        if moodValue > -0.4:
            validDomains['interrogative'] = True

        # Interrogative is always valid, so the list starts with it prepopulated
        domains = ['interrogative']
        if validDomains['declarative']:
            domains.append('declarative')
        if validDomains['imperative']:
            domains.append('imperative')
        if validDomains['simple']:
            domains.append('simple')
        if validDomains['compound']:
            domains.append('compound')
        if validDomains['interrogative']:
            domains.append('interrogative')
        # If we can generate non-interrogative sentences, we would profer to do that
        if len(domains) > 2:
            domains.remove('interrogative')

        sentence.domain = random.choice(domains)
        #sentence.domain = 'simple'
        logging.debug("Valid domains: {0}".format(str(domains)))
        logging.debug("Chose {0}".format(sentence.domain))

        # Build sentence structures
        logging.info("Building {0} structure for sentence {1} of {2}...".format(sentence.domain, i+1, len(reply)))
        if sentence.domain == 'declarative':
            sentence = make_declarative(sentence)
            sentence.contents.append(SBBPunctuation())
        elif sentence.domain == 'imperative':
            sentence = make_imperative(sentence)
            sentence.contents.append(SBBPunctuation())
        elif sentence.domain == 'interrogative':
            sentence = make_interrogative(sentence)
        elif sentence.domain == 'simple':
            sentence = make_simple(sentence)
            sentence.contents.append(SBBPunctuation())
        elif sentence.domain == 'compound':
            sentence = make_compound(sentence, random.choice(message.keywords))
            sentence.contents.append(SBBPunctuation())

    # Reorder sentences based on their domain
    # TODO: come up with a better way to do this
    reorderedReply = []
    for sentence in reply:
        if sentence.domain != 'interrogative':
            reorderedReply.append(sentence)
    for sentence in reply:
        if sentence.domain == 'interrogative':
            reorderedReply.append(sentence)
    reply = reorderedReply

    # Decide whether or not to add a greeting -- various factors contribute to a weighted coin flip
    greetingAdditionPotential = 0
    for greeting in misc.greetingStrings:
        if greeting in ' '.split(message.message)[0:3]:
            greetingAdditionPotential += 1
    if message.avgMood >= 0.2:
        greetingAdditionPotential += 1
    if moodValue >= 0.2:
        greetingAdditionPotential += 1

    # If emma's mood is low enough, destroy any chance of making a greeting
    if moodValue < -0.4:
        greetingAdditionPotential = 0

    # Do weighted coin flip to decide whether or not to add a greeting
    if random.choice(([True] * greetingAdditionPotential) + [False]):
        reply.insert(0, make_greeting(message))

    # Evaluate sentence building block objects
    for sentence in reply:
        for i, word in enumerate(sentence.contents):
            # Have/has
            if isinstance(word, SBBHaveHas):
                if sentence.isPlural:
                    sentence.contents[i] = u'have'
                else:
                    sentence.contents[i] = u'has'
            # Is/Are
            elif isinstance(word, SBBIsAre):
                logging.debug("Evaluating SBBIsAre object...")
                if sentence.isPlural:
                    sentence.contents[i] = u'are'
                else:
                    sentence.contents[i] = u'is'
            # Articles (a, the, etc.)
            elif isinstance(word, SBBArticle):
                logging.debug("Evaluating SBBArticle object...")
                validArticles = [u'the']
                if sentence.isPlural == False:
                    if sentence.contents[i+1][0] in misc.vowels:
                        validArticles.append(u'an')
                    else:
                        validArticles.append(u'a')
                else:
                    validArticles.extend([u'some', u'many'])
                sentence.contents[i] = random.choice(validArticles)
            # Conjunctions (but, and, etc.)
            elif isinstance(word, SBBConjunction):
                logging.debug("Evaluating SBBConjunction object...")
                sentence.contents[i] = random.choice([u'and', u'but', u'while'])
            # Punctuation choice is a coin flip gated by mood
            # TODO: Maybe have mood actually influence the coin flip instead of just gating it?
            elif isinstance(word, SBBPunctuation):
                logging.debug("Evaluating SBBPunctuation object...")
                canExclaim = False
                if moodValue > -0.2:
                    canExclaim = True
                if random.choice([False, canExclaim]):
                    sentence.contents[i] = u'!'
                else:
                    sentence.contents[i] = u'.'
            else:
                sentence.contents[i] = word

    # One final run to finalize the message
    finishedSentences = []
    for sentence in reply:
        # Capitalize the first letter of the sentence
        sentence.contents[0] = string.capwords(sentence.contents[0])

        for i, word in enumerate(sentence.contents):
            # Refer to Ellie as mom and Alex as dad
            if word in [u'sharkthemepark', u'deersyrup']:
                if random.choice([True, False]):
                    sentence.contents[i] = u'mom'
            elif word == u'nosiron':
                if random.choice([True, False]):
                    sentence.contents[i] = u'dad'

            # Capitalize 'Emma'
            elif word == u'emma':
                sentence.contents[i] = u'Emma'

            else:
                sentence.contents[i] = word
        
        # Turn the reply into a string
        print sentence.contents
        sentence.contents[-2] += sentence.contents[-1]
        sentence.contents.remove(sentence.contents[-1])
        finishedSentences.append(' '.join(sentence.contents))
    
    finishedReply = ' '.join(finishedSentences)
    return finishedReply