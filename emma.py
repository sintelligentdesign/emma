# -*- coding: utf-8 -*-
import random
import pickle
import logging
import os
import re
import cgi
import time

import pattern.en
import pattern.vector
import sqlite3 as sql
from disco import Plugin

import flags
import pronouns
import wordpatternfinder
import associationtrainer
import replybuilder
import misc
import apikeys

# Setup stuff
# Set up logging level (this should go in misc.py but eh)
logging.root.setLevel(logging.DEBUG)

# Pre-flight engine checks
# Check for emma.db or create it if it isn't there
logging.info("Checking for association model")
if os.path.isfile('emma.db'):
     logging.debug("Association model found!")
else:
    logging.warn("Association model not found! Creating")
    with sql.connect('emma.db') as connection:
        connection.cursor().executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, affinity DOUBLE)
        """)
    logging.debug("Association model created.")

# Set up SQL
connection = sql.connect('emma.db')
connection.text_factory = str
cursor = connection.cursor()

# Dumb chrome
print u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' \u006088b \u0060888P\"Y88bP\"Y88b  \u0060888P\"Y88bP\"Y88b  \u0060P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n\u0060Y8bod8P' o888o o888o o888o o888o o888o o888o \u0060Y888\"\"8o\n\n        ELECTRONIC MODEL of MAPPED ASSOCIATIONS\n                     Version " + misc.versionNumber + "\n"
with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print "Database contains {0} associations for {1} words.".format(associationModelItems, dictionaryItems)

# Check for and load the file containing the history of mood values or create it if it isn't there
logging.info("Loading mood history...")
if os.path.isfile('moodHistory.p'):
    logging.debug("Mood history found!")
    with open('moodHistory.p','rb') as moodFile: moodHistory = pickle.load(moodFile)
    logging.debug("Mood history loaded!")
else:   
    logging.warn("Mood history file not found! Creating...")
    with open('moodHistory.p','wb') as moodFile:
        moodHistory = [0.0] * 10
        pickle.dump(moodHistory, moodFile)
    logging.debug("Mood history file created.")

# Mood-related things
def add_mood_value(text):
    """Adds the new mood value to the front of the history list and removes the last one"""
    moodValue = pattern.en.sentiment(text)[0]
    logging.debug("Adding mood value {0} to mood history {1}...".format(moodValue, moodHistory))
    moodHistory.insert(0, moodValue)
    del moodHistory[-1]
    logging.debug("New mood history is {0}".format(moodHistory))

    # And save!
    logging.debug("Saving mood history...")
    with open('moodHistory.p', 'wb') as moodFile: 
        pickle.dump(moodHistory, moodFile)

    return moodValue

def calculate_mood():
    """Mood is calculated with a weighted mean average formula, skewed towards more recent moods"""
    logging.debug("Calculating mood...")
    # First, we calculate the weighted mood history
    weightedMoodHistory = []
    weightedMoodHistory.extend([moodHistory[0], moodHistory[0], moodHistory[0], moodHistory[1], moodHistory[1]])
    weightedMoodHistory.extend(moodHistory[2:9])

    # And take the average to get the mood
    mood = sum(weightedMoodHistory) / 13
    logging.debug("Mood: {0}".format(mood))
    return mood

def express_mood(moodValue):
    """Returns a string which can be attached to a post as a tag expressing Emma's mood"""
    logging.debug("Expressing mood...")
    if -0.8 > moodValue: 
        return u"feeling abysmal \ud83d\ude31"
    elif -0.6 > moodValue >= -0.8: 
        return u"feeling dreadful \ud83d\ude16"
    elif -0.4 > moodValue >= -0.6: 
        return u"feeling bad \ud83d\ude23"
    elif -0.2 > moodValue >= -0.4: 
        return u"feeling crummy \ud83d\ude41"
    elif 0.0 > moodValue >= -0.2: 
        return u"feeling blah \ud83d\ude15"
    elif 0.2 > moodValue >= 0.0: 
        return u"feeling alright \ud83d\ude10"
    elif 0.4 > moodValue >= 0.2: 
        return u"feeling good \ud83d\ude42"
    elif 0.6 > moodValue >= 0.4: 
        return u"feeling great \ud83d\ude09"
    elif 0.8 > moodValue >= 0.6: 
        return u"feeling fantastic \ud83d\ude00"
    elif moodValue >= 0.8: 
        return u"feeling glorious \ud83d\ude1c"

# Preparing our datatypes
# Let's start by defining some classes for NLU stuff:
class Word:
    """
    Defines a word and its attributes

    Class variables:
    word            str     String representation of the Word
    lemma           str     String representation of the root form of the Word
    partOfSpeech    str     Penn Treebank II part-of-speech tag
    chunk           str     Part of the Sentence (noun-phrase, verb-phrase, etc.)
    subjectObject   str     If the Word is a noun, this indicates whether it is the subject or object of the Sentence
    index           int     The word's position in the sentence (0-indexed)
    """

    def __init__(self, word, index):
        self.word = word[0]
        self.lemma = word[5]
        self.partOfSpeech = word[1]
        self.chunk = word[2]
        self.subjectObject = word[4]
        self.index = index

    def __str__(self): 
        return self.word

class Sentence:
    """
    Defines a sentence and its attributes, auto-generates and fills itself with Word objects

    Class variables:
    sentence                str                     String representation of the Sentence
    words                   list                    Ordered list of Word objects in the Sentence
    mood                    float                   Positive or negative sentiment in the Sentence
    length                  int                     Length of the sentence
    domain                  str                     The sentence's domain as determined by the wordpatternfinder module
    interrogativePackage    InterrogativePackage    If the sentence domain is INTERROGATIVE, this represents the question that they're asking
    """

    def __init__(self, sentence):
        self.sentence = sentence
        self.words = []
        self.mood = add_mood_value(self.sentence)
        self.length = int
        self.domain = str
        self.interrogativePackage = None

        # Get a list of Word objects contained in the Sentence and put them in taggedWords
        for i, word in enumerate(pattern.en.parse(
            self.sentence,
            tokenize = False, 
            tags = True, 
            chunks = True, 
            relations = True, 
            lemmata = True, 
            encoding = 'utf-8'
        ).split()[0]):
            self.words.append(Word(word, i))
        self.length = len(self.words)

    def __str__(self): 
        return self.sentence

class Message:
    """
    Defines a collection of Sentences and its attributes, auto-generates and fills itself with Sentence objects

    Class Variables
    message         str     String representation of the Message
    sentences       list    Ordered list of Sentence objects in the Message
    avgMood         float   Average of the mood value of all the Sentences in the Message
    keywords        list    The message's main topics
    sender          str     The name of the person who sent the message
    """

    def __init__(self, message, sender=(u'Anonymous')):
        self.message = message
        self.sentences = []
        self.avgMood = int
        self.keywords = []
        self.sender = sender

        # Get a list of Sentence objects contained in the Message and put them in taggedSentences
        for sentence in pattern.en.parse(
            self.message, 
            tokenize = True, 
            tags = False, 
            chunks = False, 
            relations = False, 
            lemmata = False, 
            encoding = 'utf-8'
        ).split('\n'):
            self.sentences.append(Sentence(sentence))

        # Average Sentence moods and record the value
        moods = []
        for sentence in self.sentences: 
            moods.append(sentence.mood)
        self.avgMood = sum(moods) / len(moods)

        # Find sentences' domains and InterrogativePackages (if applicable)
        for sentence in self.sentences:
            sentence = wordpatternfinder.find_patterns(sentence)

        # Use pattern.vector to find keywords
        for keyword in pattern.vector.Document(self.message).keywords():
            keyword = pattern.en.lemma(keyword[1])
            self.keywords.append(keyword)

        # If pattern.vector couldn't find any keywords, use the old method
        if self.keywords == []:
            logging.warning("No keywords detected by pattern.en. Using old method...")
            for sentence in self.sentences:
                for word in sentence.words:
                    if word.partOfSpeech in misc.nounCodes and word.lemma not in self.keywords:
                        self.keywords.append(word.lemma)

        # Check keywords against words that we have in the dictionary
        with connection:
            cursor.execute('SELECT * FROM dictionary;')
            dictionary = []
            for row in cursor.fetchall():
                dictionary.append(row[0])

        for keyword in self.keywords:
            if keyword not in dictionary:
                logging.debug("Removing unknown word {0} from keyword list".format(keyword))
                self.keywords.remove(keyword)

        # If we don't have any keywords, that's bad
        if self.keywords == []:
            logging.error("No keywords detected in message! This will cause a critical failure when we try to reply!")

    def __str__(self): 
        return self.message

def train(message):
    """Read a message as a string, learn from it, store what we learned in the database"""
    logging.info("Consuming message...")
    message = pronouns.determine_pronoun_references(message)
    message = pronouns.determine_posessive_references(message)

    logging.info("Looking for new words...")
    # Gather words we already know from database
    with connection:
        cursor.execute('SELECT * FROM dictionary;')

        knownWords = []
        for row in cursor.fetchall():
            knownWords.append((row[0], row[1]))     # (lemma, POS)

        # Compare them against each word from the message
        for sentence in message.sentences:
            for word in sentence.words:
                if word.partOfSpeech not in misc.trashPOS:
                    # If it's a word we don't have in the database, add it
                    #TODO: check the types of word.lemma and knownWord because apparently they aren't the same
                    if word.lemma not in [knownWord[0] for knownWord in knownWords if word.lemma == knownWord[0]]:
                        logging.info("Learned new word: \'{0}\'!".format(word.lemma.encode('utf-8', 'ignore')))
                        logging.debug("Prev. word POS: \'{0}\'".format(word.partOfSpeech))
                        knownWords.append((word.lemma, word.partOfSpeech))
                        with connection:
                            cursor.execute('INSERT INTO dictionary VALUES (\"{0}\", \"{1}\", 0);'.format(re.escape(word.lemma.encode('utf-8', 'ignore')), word.partOfSpeech))

    logging.info("Finding associations...")
    associationtrainer.find_associations(message)

def filter_message(messageText):
    """Make it easier for the computer to read messages (and also screen out banned words)"""
    # Add punctuation is it isn't already present
    if messageText[-1] not in ['!', '?', '.']:
        messageText += "."

    # Translate internet slang and fix weird parsing stuff
    filtered = []
    for word in messageText.split(' '):
        word = word.decode('utf-8')
        # Translate internet abbreviations
        if word.lower() in misc.netspeak.keys():
            logging.debug("Translating \'{0}\' from net speak...".format(word))
            filtered.extend(misc.netspeak[word.lower()])
        # Change "n't" to "not"
        elif word.lower() in [u"n\'t", u"n\u2019t", u"n\u2018t"]:
            logging.debug("Replacing \"n\'t\" with \"not\"...")
            filtered.append(u'not')
        # Remove "'s"
        elif word.lower() == u"\'s":
            pass
        # Remove double quote characters
        elif "\"" in word or u"“" in word or u"”" in word:
            pass
        else:
            filtered.append(word)
    filteredText = ' '.join(filtered)

    return filteredText

class Ask:
    def __init__(self, message, sender, askid):
        self.sender = sender
        self.askid = askid
        self.message = message.encode('utf-8', 'ignore')
        self.message = filter_message(self.message)
        self.message = Message(self.message, self.sender)

if flags.enableDebugMode == False:
    # Authenticate with Tumblr API
    client = pytumblr.TumblrRestClient(
        apikeys.tumblrConsumerKey,
        apikeys.tumblrConsumerSecret,
        apikeys.tumblrOauthToken,
        apikeys.tumblrOauthSecret
    )
    blogName = 'emmacanlearn'

    while True:
        logging.info("Checking Tumblr messages...")
        response = client.submission(blogName)
        if len(response['posts']) > 0:
            asks = []
            for ask in response['posts']:
                asks.append(Ask(ask['question'], ask['asking_name'], ask['id']))

            # Choose a selection of asks to answer
            askRange = random.randint(2, 4)
            if len(asks) <= 4:
                askRange = len(asks)
            asks = asks[len(asks) - askRange:]
            logging.info("Answering {0} asks...".format(askRange))

            for ask in asks:
                logging.debug("@{0} says: {1}".format(ask.sender, ask.message.message.encode('utf-8', 'ignore')))

                # Look for profanity or banned words
                with open('bannedwords.txt', 'r') as bannedWords:
                    bannedWords = bannedWords.read()
                    bannedWords = bannedWords.split('\n')
                    
                    for word in ask.message.message.split(' '):

                        profanity = []
                        profanity.extend(pattern.en.wordlist.PROFANITY)
                        profanity.remove('gay')

                        if word.lower() in bannedWords:
                            logging.info("Banned word found in message. Deleting...")
                            client.delete_post(blogName, ask.askid)
                            pass
                        elif word.lower() in profanity:
                            logging.info("Profane word found in message. Deleting...")
                            client.delete_post(blogName, ask.askid)
                            pass

                # Learn from and reply to the ask
                train(ask.message)
                reply = replybuilder.reply(ask.message, calculate_mood())
                if reply == 0:
                    # Sentence generation failed
                    client.delete_post(blogName, ask.askid)
                    pass
                else:
                    reply = cgi.escape(reply)
                    logging.info("Reply: {0}".format(reply))

                    # Post the reply to Tumblr
                    reply = reply.encode('utf-8', 'ignore')
                    tags = ['dialogue', ask.sender.encode('utf-8', 'ignore'), express_mood(calculate_mood()).encode('utf-8', 'ignore')]
                    client.edit_post(
                        blogName,
                        id = ask.askid,
                        answer = reply,
                        state = 'published',
                        tags = tags,
                        type = 'answer'
                    )
        else:
            logging.info("No new Tumblr messages.")

        # Sleep for 10 minutes
        logging.info("Sleeping for 10 minutes...")
        time.sleep(600)

else:
    # Debug stuff
    if flags.useTestingStrings: 
        inputText = random.choice(flags.testingStrings)
    else: inputText = raw_input("Message >> ")

    message = Message(filter_message(inputText.encode('utf-8', 'ignore')), "You")
    logging.debug("Message: {0}".format(message.message))
    train(message)

    reply = replybuilder.reply(message, calculate_mood())
    if reply == 0:
        # Sentence generation failed
        pass
    else:
        print reply
