# -*- coding: utf-8 -*-

#   .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
#  d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
#  888ooo888  888   888   888   888   888   888   .oP"888
#  888    .,  888   888   888   888   888   888  d8(  888
#  `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o
#
#  ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
#
#          EXPANDING MODEL of MAPPED ASSOCIATIONS
#
#
#     Written by Ellie Cochran & Alexander Howard, with
#                contributions by Omri Barak.
import time
import random

import pattern.en
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import tumblrclient
import parse
import pronouns
import associationtrainer
import sentencebuilder
import utilities
from config import debug, console, database, tumblr

connection = sql.connect(database['path'])
cursor = connection.cursor()
print Fore.BLUE + "Checking if concept database exists at %s..." % database['path']
with connection:
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'associationmodel\';")
    SQLReturn = cursor.fetchone()
if SQLReturn != (u'associationmodel',):
    print Fore.YELLOW + "Database invalid. Creating database at %s..." % database['path']
    with connection:
        cursor.executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS sentencestructuremodel;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, is_new INTEGER DEFAULT 1, is_banned INTEGER DEFAULT 0);
        """)
    print Fore.GREEN + "Database with required schema created at %s!" % database['path']
else: 
    print Fore.GREEN + "Database valid! Continuing..."

# "Emma" banner
print Fore.MAGENTA + u" .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' `88b `888P\"Y88bP\"Y88b  `888P\"Y88bP\"Y88b  `P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n`Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888\"\"8o\n\n·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.1"
    
def consume(parsedSentence, asker=""):
    if console['verboseLogging']: print "Consuming sentence..."
    pronouns.determine_references(parsedSentence)
    pronouns.flip_posessive_references(parsedSentence, asker)
    parse.add_new_words(parsedSentence)
    associationtrainer.find_associations(parsedSentence)
    if console['verboseLogging']: print "Sentence consumed."

class moodStack(list):
    def push(self, item):
        self.insert(0, item)
        self.remove(self[10])
moodModifiers = moodStack([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
mood = 0

def calculate_mood(text):
    moodModifiers.push(reduce(lambda x, y: x * y, pattern.en.sentiment(text)))
    if console['verboseLogging']: print "Mood modifiers: " + str(moodModifiers)
    return sum(moodModifiers) / 10

def reply_to_asks(messageList):

    if len(messageList) > 0:
        print "Fetched %d new asks." % len(messageList)
        for askCount, message in enumerate(messageList):
            # todo: intelligently decide how many asks to answer
            print "Reading ask no. %d of %d..." % (askCount + 1, len(messageList))
            print Fore.BLUE + u"@" + message[1] + u" >> " + message[2]

            mood = calculate_mood(message[2])

            parsedMessage = parse.tokenize(message[2])

            for sentenceCount, sentence in enumerate(parsedMessage):
                if console['verboseLogging']: print "Reading sentence no. %d of ask no. %d..." % ((sentenceCount + 1), (askCount + 1))
                consume(sentence, message[1])
            
            emmaUnderstanding = u""
            for sentenceCount, sentence in enumerate(parsedMessage):
                for wordCount, word in enumerate(sentence):
                    if wordCount == 0 and sentenceCount != 0:
                        emmaUnderstanding += u" "
                    emmaUnderstanding += word[0]
                    if wordCount < len(sentence) - 2:
                        emmaUnderstanding += u" "
            emmaUnderstanding = u"Emma interpreted this message as: \'%s\'" % emmaUnderstanding
            print Fore.BLUE + emmaUnderstanding

            reply = sentencebuilder.generate_sentence(parsedMessage)

            greet = False
            for keyword in utilities.greetingTerms:
                print Fore.RED + u'line 171 %s' % keyword
                if parse.find_whole_words(keyword, message[2]):
                    print 'line 173'
                    greet = True
                    break
            if greet:
                reply = reply[0].lower() + reply[1:]
                reply = random.choice(utilities.greetingTerms) + ", @" + message[1] + ", " + reply

            if "%" not in reply:
                print Fore.BLUE + u"emma >> %s" % reply
                mood = calculate_mood(reply)
                    
                print "Posting reply..."
                # Reply bundle is (asker, question, response, debugInfo)
                # todo: remove debugInfo when we enter Beta (?)
                tumblrclient.post_reply(message[1], message[2], reply, (emmaUnderstanding, mood))
            else:
                print Fore.YELLOW + "Sentence generation failed."

            tumblrclient.delete_ask(message[0])

            if debug['enableSleep']:
                print "Sleeping for 3 minutes..."
                time.sleep(180)
            else:
                print Fore.YELLOW + "!!! Sleep disabled in config file -- execution will continue normally in 2 seconds..."
                time.sleep(2)

def dream():
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_banned = 0 ORDER BY RANDOM() LIMIT 10;')
        SQLReturn = cursor.fetchall()
    dreamSeed = ""
    for word in SQLReturn:
        dreamSeed += word[0] + " "
    print "Dream seed: " + dreamSeed
    dream = sentencebuilder.generate_sentence(pattern.en.parse(dreamSeed, True, True, True, True, True).split())
    if "%" not in dream:
        print Fore.BLUE + u"dream >> " + dream
        tumblrclient.post_dream(dream)
    else: print Fore.YELLOW + "Dreamless sleep..."

def chat():
    print Fore.YELLOW + "!!! Chat mode enabled in config file. Press Control-C to exit."
    while True:
        tokenizedMessage = parse.tokenize(raw_input(Fore.BLUE + 'You >> ').decode('utf-8'))
        for sentence in tokenizedMessage:
            consume(sentence)
        # todo: if sentence generation fails, what's a good way to let the user know?
        reply = sentencebuilder.generate_sentence(tokenizedMessage)
        print Fore.BLUE + u"emma >> " + reply

while True:
    if console['chatMode']: chat()
    else:
        print "Choosing activity..."
        if debug['fetchRealAsks']: messageList = tumblrclient.get_messages()
        else: 
            print Fore.YELLOW + "!!! Real ask fetching disabled in config file. Using fake asks instead -- execution will continue with sample Asks provided in 2 seconds..."
            time.sleep(2)
            messageList = debug[fakeAsks]

        if messageList != []: 
            print "Replying to messages..."
            reply_to_asks(messageList)
        else:
            print "Dreaming..."
            dream()
        
        if debug['enableSleep']:
            print "Sleeping for 10 minutes..."
            time.sleep(600)
        else:
            print Fore.YELLOW + "!!! Sleep disabled in config file -- execution will continue normally in 2 seconds..."
            time.sleep(2)