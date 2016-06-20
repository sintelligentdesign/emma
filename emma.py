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

import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import tumblrclient
import parse
import markovtrainer
import pronouns
import associationtrainer
import sentencebuilder
import utilities
from config import console, database, tumblr


lastDreamTime = time.clock()

lastFourActivites = [None, None, None, None]

connection = sql.connect(database['path'])
cursor = connection.cursor()
# Check to see if our database is valid and, if not, create one that is
if console['verboseLogging']: print Fore.BLUE + "Checking validity of database %s" % database['path']
with connection:
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'associationmodel\' OR name=\'dictionary\' OR name=\'sentencestructuremodel\';')
    SQLReturn = cursor.fetchall()
if SQLReturn != [(u'dictionary',), (u'sentencestructuremodel',), (u'associationmodel',)]: 
    if console['verboseLogging']: print Fore.YELLOW + "Database invalid. Creating default tables in %s..." % database['path']
    with connection:
        cursor.executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS sentencestructuremodel;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, is_new INTEGER DEFAULT 1, is_banned INTEGER DEFAULT 0);
        CREATE TABLE sentencestructuremodel(stem TEXT, leaf TEXT, weight DOUBLE, is_sentence_starter INTEGER DEFAULT 0);
        """)
    if console['verboseLogging']: print Fore.GREEN + "Default database created at %s!" % database['path']
else: 
    if console['verboseLogging']: print Fore.GREEN + "Database valid! Continuing..."

def main(lastFourActivites, lastDreamTime):
    lastFourActivites, lastDreamTime = choose_activity(lastFourActivites, lastDreamTime)
    return lastFourActivites, lastDreamTime
    
def consume(parsedSentence, asker):
    parse.add_new_words(parsedSentence)
    markovtrainer.train(parsedSentence)
    #pronouns.decode_references(parsedSentence)
    pronouns.flip_posessive_references(parsedSentence, asker)
    associationtrainer.find_associations(parsedSentence)

    emmaUnderstanding = ""

    print "Sentence consumed."

def choose_activity(lastFourActivites, lastDreamTime):
    with connection:
        cursor.execute('SELECT * FROM dictionary WHERE is_new = 1')
        newWords = len(cursor.fetchall())
    newAsks = len(tumblrclient.get_messages())
    timeElapsedSinceLastDream = time.clock() - lastDreamTime
    activities = ["reply", "learn words", "dream"]

    # Count how many times each activity was done in the last four times.
    countActivities = {activity:lastFourActivites.count(activity) for activity in lastFourActivites}

    # Decide what emma wants to do
    if newAsks == 0 and newWords == 0:
        lastDreamTime = time.clock()
        dream()
        del lastFourActivites[0]
        lastFourActivites.append("dream")
    
    elif timeElapsedSinceLastDream > 1800:
        lastDreamTime = time.clock()
        dream()
        del lastFourActivites[0]
        lastFourActivites.append("dream")
        
    elif ("reply" not in countActivities or countActivities["reply"] <= 1 ) and newAsks > 0:
        reply_to_asks()
        del lastFourActivites[0]
        lastFourActivites.append("reply")
        
    elif ("learn words" not in countActivities or countActivities["learn words"] <= 1 ) and newWords > 0:
        learn_new_words()
        del lastFourActivites[0]
        lastFourActivites.append("learn words")
        
    elif newAsks > 5:
        reply_to_asks()
        del lastFourActivites[0]
        lastFourActivites.append("reply")
        
    elif newWords > 5:
        learn_new_words()
        del lastFourActivites[0]
        lastFourActivites.append("learn words")
        
    else:
        lastDreamTime = time.clock()
        dream()
        del lastFourActivites[0]
        lastFourActivites.append("dream")

    return lastFourActivites, lastDreamTime

def reply_to_asks():
    #messageList = tumblrclient.get_messages()
    messageList = [("12345", "asker", u"I think you're fantastic. I don't know what I'd do without you.")]
    if len(messageList) > 0:
        print "Fetched %d new asks" % len(messageList)
        for count, message in enumerate(messageList):
            print "Reading ask no. %d..." % (count + 1)
            # todo: intelligently decide how many asks to answer
            print Fore.BLUE + u"@" + message[1] + u" >> " + message[2]

            parsedMessage = parse.tokenize(message[2])

            for sentence in parsedMessage:
                consume(sentence, message[1])
            
            emmaUnderstanding = u""
            for sentenceCount, sentence in enumerate(parsedMessage):
                for wordCount, word in enumerate(sentence):
                    if wordCount == 0 and sentenceCount != 0:
                        emmaUnderstanding += u" "
                    emmaUnderstanding += word[0]
                    if wordCount < len(sentence) - 2:
                        emmaUnderstanding += u" "
            emmaUnderstanding = u"Emma parsed this ask as: \'%s\'" % emmaUnderstanding
            print Fore.BLUE + emmaUnderstanding

            reply, importantWords, relatedWords = sentencebuilder.generate_sentence(parsedMessage)
            if reply:
                reply = ' '.join(reply)
                print Fore.BLUE + u"emma >> %s" % reply

                # todo: remove debug reply
                reply = reply + "\n" + "importantWords: " + str(importantWords) + "\n" + "relatedWords: " + str(relatedWords)
                
                print "Posting reply..."
                # Reply bundle is (asker, question, response, debugInfo)
                # todo: remove debugInfo when we enter Beta (?)
                tumblrclient.post_reply(message[1], message[2], reply, emmaUnderstanding)

            else: print Fore.YELLOW + "No reply."
            if tumblr['deleteAsks']:
                print "Deleting ask..."
                tumblrclient.delete_ask(message[0])
            else:
                print Fore.YELLOW + "!!! Ask deletion disabled in config.py -- execution will continue normally in 2 seconds..."
                time.sleep(2)

            print "Sleeping for 10 seconds..."
            time.sleep(10)
    else:
        print "No new asks :("

def learn_new_words():
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_new = 1;')
        newWords = cursor.fetchall()
    if newWords:
        # todo: intelligently choose a number of words to learn
        for row in newWords:
            word = row[0]
            word = word.decode('utf-8')
            results = tumblrclient.search_for_text_posts(word)
            for result in results:
                if not u".com" in result:      # This does an ok job of filtering out results from spam bots
                    tokenizedResult = parse.tokenize(result)
                    if tokenizedResult:
                        consume(tokenizedResult)
            with connection:
                cursor.execute("UPDATE dictionary SET is_new = 0 WHERE word = \"%s\";" % word)
        
# todo: remove these debug function calls
reply_to_asks()
#learn_new_words()

def dream():
    print "Dreaming..."
    for i in range(8):      # todo: semi-logically choose how many dreams to dream
        with connection:
            cursor.execute('SELECT word FROM dictionary WHERE is_new = 0 AND is_banned = 0 ORDER BY RANDOM() LIMIT 3;')
            SQLReturn = cursor.fetchall()
        # todo: generate a sentence 
        dream = "sentence"
        tumblrclient.post_dream(dream)
        print Fore.BLUE + u"dream >> " + dream
        consume(dream)
        time.sleep(5)

# while True:
#     lastFourActivites, lastDreamTime = main(lastFourActivites, lastDreamTime)
#     print "Sleeping for 10 seconds..."
#     time.sleep(10)