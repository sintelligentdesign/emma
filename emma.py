import random
import pickle
import logging
import os

import pattern.en
import sqlite3 as sql

import misc
import flags

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

# Preparing our datatypes
# Let's start by defining some classes to hold input stuff:
class Word:
    def __init__(self, word):
        self.originalWord = word[0]
        self.lemma = word[5]
        self.partOfSpeech = word[3]
        self.chunk = word[2]
        self.subjectObject = word[4]

class Sentence:
    def __init__(self, sentence):
        self.sentence = sentence
        self.taggedWords = []
        self.mood = float

    # Returns a list of Word objects contained in the Sentence
    def get_words(self):
        for taggedWord in self.sentence:
            self.taggedWords.append(Word(taggedWord))
        return self.taggedWords

class Message:
    def __init__(self, message):
        self.message = message
        self.taggedSentences = []
        self.avgMood = float
        self.domain = ''

    # Returns a list of Sentence objects contained in the Message
    def get_sentences(self):
        for taggedSentence in pattern.en.parse(self.message, True, True, True, True, True).split(): 
            self.taggedSentences.append(Sentence(taggedSentence))
        return self.taggedSentences

class Question:
    def __init__(self):
        return

class ImportantWord:
    def __init__(self):
        return

# Input is stored as a Message object
if flags.useTestingStrings: inputMessage = Message(random.choice(flags.testingStrings))
else: inputMessage = Message(input("Message >> "))

sentences = inputMessage.get_sentences()
words = sentences[0].get_words()

# Mood-related things
# Adds the new mood value to the front of the history list and removes the last one
def add_mood_value(text):
    moodValue = pattern.en.sentiment(text)[0]
    logging.debug('Adding mood value %s to mood history %s...' % (moodValue, moodHistory))
    moodHistory.insert(0, moodValue)
    del moodHistory[-1]
    logging.debug('New mood history is %s' % moodHistory)

    # And save!
    logging.info('Saving new mood history...')
    with open('moodhistory.p', 'wb') as moodFile: 
        pickle.dump(moodHistory, moodFile)
    return moodHistory

# Mood is calculated with a weighted mean average formula, skewed towards more recent moods
def calculate_mood():
    logging.debug('Calculating mood...')
    # First, we calculate the weighted mood history
    weightedMoodHistory = []
    weightedMoodHistory.extend([moodHistory[0], moodHistory[0], moodHistory[0], moodHistory[1], moodHistory[1]])
    weightedMoodHistory.extend(moodHistory[2:9])

    # And take the average to get the mood
    mood = sum(weightedMoodHistory) / 13
    return mood

# Returns a string which can be attached to a post as a tag expressing Emma's mood
def express_mood(moodValue):
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

# Checking that mood works
#print add_mood_value("I'm so happy!")
#print calculate_mood()
#print express_mood(calculate_mood())

# Read a message as a string, learn from it, store what we learned in the database
def consume(messageText):
    inputMessage = Message(messageText)
    inputSentences = inputMessage.get_sentences()

    for inputSentence in inputSentences.sentences:
        inputWords = inputSentence.get_words()
        # TODO: All of this
        # Read the words
        # Determine pronoun references
        # Determine domain
            # If interrogative, check for Question objects
            # Otherwise,
        # Look for ImportantWord objects
        # Add new words to the dictionary
        # Write to db
        # Find associations
        # Write to db

# Read a message as a Message object and reply to it
def reply(message):
    # Look up ImportantWords and Questions
    # Find their associations/answers
    # Generate a reply
    # Return