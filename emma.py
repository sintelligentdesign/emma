import random
import pickle
import logging
import os
import re

import pattern.en
import pattern.vector
import sqlite3 as sql

import flags
import pronouns
import associationtrainer
import misc

# Dumb chrome
misc.show_emma_banner()
misc.show_database_stats()

# Setup stuff
# Set up SQL (this is used a LOT throughout the code)
connection = sql.connect('emma.db')
cursor = connection.cursor()

# Set up logging level (this should go in misc.py but eh)
logging.root.setLevel(logging.INFO)

# Pre-flight engine checks
# Check for emma.db or create it if it isn't there
logging.info('Checking for database...')
if os.path.isfile('emma.db'): logging.debug('Database found!')
else:
    logging.warn('Database not found! Eventually this will create a new database but for now you have to do it by hand...')
    # TODO: Create a new database if one cannot be found

# Check for and load the file containing the history of mood values or create it if it isn't there
logging.info('Loading mood history...')
if os.path.isfile('moodHistory.p'):
    logging.debug('Mood history found!')
    with open('moodHistory.p','rb') as moodFile: moodHistory = pickle.load(moodFile)
    logging.debug('Mood history loaded!')
else:   
    logging.warn('Mood history file not found! Creating...')
    with open('moodHistory.p','wb') as moodFile:
        moodHistory = [0] * 10
        pickle.dump(moodHistory, moodFile)
    logging.debug('Mood history file creation done.')

# Mood-related things
def add_mood_value(text):
    """Adds the new mood value to the front of the history list and removes the last one"""
    moodValue = pattern.en.sentiment(text)[0]
    logging.debug('Adding mood value %s to mood history %s...' % (moodValue, moodHistory))
    moodHistory.insert(0, moodValue)
    del moodHistory[-1]
    logging.debug('New mood history is %s' % moodHistory)

    # And save!
    logging.info('Saving mood history...')
    with open('moodhistory.p', 'wb') as moodFile: 
        pickle.dump(moodHistory, moodFile)

    return moodValue

def calculate_mood():
    """Mood is calculated with a weighted mean average formula, skewed towards more recent moods"""
    logging.debug('Calculating mood...')
    # First, we calculate the weighted mood history
    weightedMoodHistory = []
    weightedMoodHistory.extend([moodHistory[0], moodHistory[0], moodHistory[0], moodHistory[1], moodHistory[1]])
    weightedMoodHistory.extend(moodHistory[2:9])

    # And take the average to get the mood
    mood = sum(weightedMoodHistory) / 13
    logging.debug('Mood: %d' % mood)
    return mood

def express_mood(moodValue):
    """Returns a string which can be attached to a post as a tag expressing Emma's mood"""
    logging.debug('Expressing mood...')
    if -0.8 > moodValue: return u"feeling abysmal \ud83d\ude31"
    elif -0.6 > moodValue >= -0.8: return u"feeling dreadful \ud83d\ude16"
    elif -0.4 > moodValue >= -0.6: return u"feeling bad \ud83d\ude23"
    elif -0.2 > moodValue >= -0.4: return u"feeling crummy \ud83d\ude41"
    elif 0.0 > moodValue >= -0.2: return u"feeling blah \ud83d\ude15"
    elif 0.2 > moodValue >= 0.0: return u"feeling alright \ud83d\ude10"
    elif 0.4 > moodValue >= 0.2: return u"feeling good \ud83d\ude42"
    elif 0.6 > moodValue >= 0.4: return u"feeling great \ud83d\ude09"
    elif 0.8 > moodValue >= 0.6: return u"feeling fantastic \ud83d\ude00"
    elif moodValue >= 0.8: return u"feeling glorious \ud83d\ude1c"

# Preparing our datatypes
# Let's start by defining some classes for NLU stuff:
class Word:
    """
    Defines a word and its attributes

    Class variables:
    word          str     String representation of the Word
    lemma         str     String representation of the root form of the Word
    partOfSpeech  str     Penn Treebank II part-of-speech tag
    chunk         str     Part of the Sentence (noun-phrase, verb-phrase, etc.)
    subjectObject str     If the Word is a noun, this indicates whether it is the subject or object of the Sentence
    """

    def __init__(self, word):
        self.word = word[0]
        self.lemma = word[5]
        self.partOfSpeech = word[3]
        self.chunk = word[2]
        self.subjectObject = word[4]

    def __str__(self): return self.word

class Sentence:
    """
    Defines a sentence and its attributes, auto-generates and fills itself with Word objects

    Class variables:
    sentence      str     String representation of the Sentence
    words         list    Ordered list of Word objects in the Sentence
    mood          float   Positive or negative sentiment in the Sentence
    """

    def __init__(self, sentence):
        self.sentence = sentence

        # Get a list of Word objects contained in the Sentence and put them in taggedWords
        self.words = []
        for word in pattern.en.parse(
            self.sentence,
            tokenize = False, 
            tags = True, 
            chunks = True, 
            relations = True, 
            lemmata = True, 
            encoding = 'utf-8'
        ).split()[0]:
            self.words.append(Word(word))

        # Get the mood of the Sentence
        self.mood = add_mood_value(self.sentence)

    def __str__(self): return self.sentence

class Message:
    """
    Defines a collection of Sentences and its attributes, auto-generates and fills itself with Sentence objects

    Class Variables
    message       str     String representation of the Message
    sentences     list    Ordered list of Sentence objects in the Message
    avgMood       float   Average of the mood value of all the Sentences in the Message
    """

    def __init__(self, message):
        self.message = message
        self.sentences = []
        self.avgMood = int
        self.keywords = pattern.vector.Document(self.message).keywords()

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

    def __str__(self): return self.message

def filter_message(messageText):
    """Make it easier for the computer to read messages (and also screen out banned words)"""
    # Add punctuation is it isn't already present
    if messageText[-1] not in [u'!', u'?', u'.']:
        messageText += u"."

    # Translate internet slang and remove bad words
    filtered = []
    for word in messageText.split(' '):
        if word.lower() in misc.netspeak.keys():
            logging.debug("Translating \'%s\' from net speak..." % word)
            filtered.append(misc.netspeak[word.lower()])
        elif word.lower() in pattern.en.wordlist.PROFANITY:
            pass
        else:
            filtered.append(word)
    filteredText = ' '.join(filtered)

    return filteredText

def train(messageText, sender="You"):
    """Read a message as a string, learn from it, store what we learned in the database"""
    message = Message(filter_message(messageText))

    logging.info("Consuming message...")
    message = pronouns.determine_pronoun_references(message)
    message = pronouns.determine_posessive_references(message, sender)

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
                # If it's a word we don't have in the database, add it
                if word.lemma not in [knownWord[0] for knownWord in knownWords if word.lemma == knownWord[0]]:
                    logging.info("Learned new word: \'%s\'!" % word.lemma)
                    knownWords.append((word.lemma, word.partOfSpeech))
                    with connection:
                        cursor.execute('INSERT INTO dictionary VALUES (\"%s\", \"%s\", 0);' % (re.escape(word.lemma), word.partOfSpeech))

    # TODO: All of this
    # Find associations
    # Write to db

# Read a message as a Message object and reply to it
class Association:
    # note for self: does there need to be an option or word being a Word object? couldn't the program just pass Word.lemma or something
    def __init__(self, word):
        if type(word) == "str":
            # Handle as string
            pass
        else:
            # Handle as Word object
            pass

def reply(message):
    # Look up ImportantWords and Questions
    # Find their associations/answers
    # Generate a reply
    return

# Input is stored as a Message object
if flags.useTestingStrings: inputText = random.choice(flags.testingStrings)
else: inputText = input("Message >> ")
train(inputText)