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

import tumblrclient as tumblr
import parse
import markovtrainer
import antecedentfiller
import associationtrainer
import sentencebuilder
import utilities

lastDreamTime = time.clock()

lastFourActivites = [None, None, None, None]

connection = sql.connect('emma.db')
cursor = connection.cursor()

def main(lastFourActivites, lastDreamTime):
    lastFourActivites, lastDreamTime = choose_activity(lastFourActivites, lastDreamTime)
    return lastFourActivites, lastDreamTime
    
def consume(sentence):
    # todo: iterate through sentence items here instead of in the functions we call
    parse.add_new_words(sentence)
    markovtrainer.train(sentence)
    #antecedentfiller.determine_references(sentence)        # todo: uncomment once antecedentfiller is complete
    associationtrainer.find_associations(sentence)
    print "Sentence consumed."

def choose_activity(lastFourActivites, lastDreamTime):
    with connection:
        cursor.execute('SELECT * FROM dictionary WHERE is_new = 1')
        newWords = len(cursor.fetchall())
    newAsks = len(tumblr.get_messages())
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
    #messageList = tumblr.get_messages()
    messageList = [("12345", "asker", u"I\u2019m afraid that the doctor\u2019s cure isn\u2019t working.")]
    if len(messageList) > 0:
        print "Fetched %d new asks" % len(messageList)
        for count, message in enumerate(messageList):
            # todo: intelligently decide how many asks to answer
            print u"@" + message[1] + u" >> " + message[2]

            tokenizedMessage = parse.tokenize(message[2])
            consume(tokenizedMessage)

            reply = sentencebuilder.generate_sentence(tokenizedMessage)
            reply = ' '.join(reply)
            print u"emma >> %s" % reply
            
            tumblr.post_reply(message[1], message[2], reply)
            tumblr.delete_ask(message[0])
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
            results = tumblr.search_for_text_posts(word)
            for result in results:
                tokenizedResult = parse.tokenize(result)
                if tokenizedResult:
                    consume(tokenizedResult)
            with connection:
                cursor.execute("UPDATE dictionary SET is_new = 0 WHERE word = \"%s\";" % word)
        
# todo: remove these debug function calls
reply_to_asks()
learn_new_words()

def dream():
    print "Dreaming..."
    for i in range(8):      # todo: semi-logically choose how many dreams to dream
        # todo: generate a sentence 
        dream = "sentence"
        tumblr.post_dream(dream)
        print "dream >> " + dream
        consume(dream)
        time.sleep(5)

# while True:
#     lastFourActivites, lastDreamTime = main(lastFourActivites, lastDreamTime)
#     print "Sleeping for 10 seconds..."
#     time.sleep(10)
