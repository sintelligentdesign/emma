# -*- coding: utf-8 -*-
import random
import pickle
import logging
import os
import re
import cgi
import time

import pattern.en
import sqlite3 as sql
import pytumblr

import flags
import references
import wordpatternfinder
import associationtrainer
import replybuilder
import misc
import apikeys

# Setup stuff
# Set up logging level (this should go in misc.py but eh)
logging.root.setLevel(logging.DEBUG)

# Pre-flight
# Set up SQL
connection = sql.connect('emma.db')
connection.text_factory = str   # Return bytestring instead of Unicode
cursor = connection.cursor()

# Create our database tables if they aren't there
logging.warn("Association model not found!")
with connection:
    connection.cursor().executescript("""
    CREATE TABLE IF NOT EXISTS associationmodel(word_id INTEGER NOT NULL, association_type TEXT NOT NULL, target_id INTEGER NOT NULL, weight DOUBLE NOT NULL);
    CREATE TABLE IF NOT EXISTS dictionary(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, word TEXT NOT NULL, part_of_speech TEXT NOT NULL, sentiment DOUBLE NOT NULL);
    CREATE TABLE IF NOT EXISTS verbsyntaxmodel(pre_word_id INTEGER, verb_id INTEGER NOT NULL, post_word_id INTEGER, is_transitive INTEGER NOT NULL)
    """)

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
def add_mood_value(moodValue):
    """Adds the new mood value to the front of the history list and removes the last one"""
    logging.debug("Adding mood value {0} to mood history...".format(moodValue))
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
    # TODO: constrict ranges even more?
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

class Ask:
    def __init__(self, message, sender, askid):
        self.sender = sender
        self.askid = askid
        self.message = message.encode('utf-8', 'ignore')
        self.message = filter_message(self.message)
        self.sentiment = int
        self.keywords = []

        # Get sentiment and update mood value
        self.sentiment = pattern.en.sentiment(message)[0]
        add_mood_value(self.sentiment)

    def __str__(self): 
        return self.message

def train(message, ask):
    """Read a message as a string, learn from it, store what we learned in the database"""
    logging.info("Consuming message...")

    logging.info("Looking for new words...")
    for sentence in message.sentences:
        for word in sentence.words:
            with connection:
                lemma = word.lemma
                cursor.execute('SELECT * FROM dictionary WHERE word == "{0}";'.format(lemma.encode('utf-8', 'ignore')))
                result = cursor.fetchone()
                if result:
                    # Update the affinity value
                    logging.info("Updating affinity value for '{0}'".format(lemma.encode('utf-8', 'ignore')))
                    cursor.execute('UPDATE dictionary SET sentiment = {0} WHERE id = {1}'.format((result[3]+ask.sentiment)/2, result[0]))
                else:
                    # Add the word to the dictionary
                    logging.info("Learned new word: '{0}'!".format(lemma.encode('utf-8', 'ignore')))
                    cursor.execute('INSERT INTO dictionary (word, part_of_speech, sentiment) VALUES ("{0}", "{1}", {2})'.format(lemma.encode('utf-8', 'ignore'), word.type, ask.sentiment))

    logging.info("Finding associations...")
    # associationtrainer.find_associations(message)

def filter_message(messageText):
    """Make it easier for the computer to read messages (and also screen out banned words)"""
    # Add punctuation is it isn't already present
    if messageText[-1] not in ['!', '?', '.']:
        messageText += "."

    # Translate internet slang and fix weird parsing stuff
    netspeak = {
        u'aight': [u'alright'],
        u'btw': [u'by', u'the', u'way'],
        u'cn': [u'can'],
        u'gonna': [u'going', u'to'],
        u'im': [u'I\'m'],
        u'imo': [u'in', u'my', u'opinion'],
        u'lemme': [u'let', u'me'],
        u'n': [u'and'],
        u'obv': [u'obviously'],
        u'omg': [u'oh', u'my', u'god'],
        u'r': [u'are'],
        u'k': [u'okay'],
        u'tbh': [u'to', u'be', u'honest'],
        u'tbqh': [u'to', u'be', u'quite', u'honest'],
        u'u': [u'you'],
        u'ur': [u'your'],
        u'yr': [u'your'],
        u'yea': [u'yeah'],
        u'ya': [u'yeah']
    }
    filtered = []
    for word in messageText.split(' '):
        word = word.decode('utf-8')
        # Translate internet abbreviations
        if word.lower() in netspeak.keys():
            logging.debug("Translating \'{0}\' from net speak...".format(word))
            filtered.extend(netspeak[word.lower()])
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

                    profanity = []
                    profanity.extend(pattern.en.wordlist.PROFANITY)
                    profanity.remove('gay')
                    profanity.remove('queer')
                    
                    for word in ask.message.message.split(' '):
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

    ask = Ask(inputText, 'sender', 000)

    # Filter message
    inputText = filter_message(inputText)

    # Tokenize input unicode str
    tokenizedText = pattern.en.parsetree(
        inputText,
        tokenize = True,
        tags = True,
        chunks = True,
        relations = False,
        lemmata = True,
        encoding = 'utf-8'
    )

    # Determine references
    inputText = references.determine_references(tokenizedText, ask)

    # Retokenize text since it has references now
    # TODO: make this a function so we're not repeating code
    tokenizedText = pattern.en.parsetree(
        inputText,
        tokenize = True,
        tags = True,
        chunks = True,
        relations = False,
        lemmata = True,
        encoding = 'utf-8'
    )

    logging.debug("Tokenized message: {0}".format(tokenizedText.string))
    train(tokenizedText, ask)

    # Get keywords from the message so we know what to use in our reply
    # Use pattern.vector to find keywords
    logging.info("Finding keywords...")

    keywords = []
    for sentence in tokenizedText:
        for word in sentence.words:
            if word.type in misc.nounCodes:
                keywords.append(word.lemma)

    # If we don't have any keywords, that's bad
    # TODO: Think of a way to reply without keywords?
    if keywords == []:
        logging.error("No keywords detected in message! This will cause a critical failure when we try to reply!")

    logging.info("Message keyword(s): {0}".format(', '.join(keywords)))

    reply = replybuilder.reply(message, calculate_mood())
    if reply == 0:
        # Sentence generation failed
        pass
    else:
        print reply