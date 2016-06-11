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
    # get number of new words
    with connection:
        cursor.execute('SELECT * FROM dictionary WHERE is_new = 1')
        newWords = len(cursor.fetchall())

    # get number of new tumblr asks
    newAsks = len(tumblr.get_messages())

    # get time elapsed since last dream period
    timeElapsedSinceLastDream = time.clock() - lastDreamTime

    # get bias
    activities = ["reply", "learn words", "dream"]

    # count how many times each activity was don in the last four times.
    countActivities = {activity:lastFourActivites.count(activity) for activity in lastFourActivites}

    # decide what emma wants to do
    if newAsks == 0 and newWords == 0:
        # dream
        lastDreamTime = time.clock()
        dream()
        del lastFourActivites[0]
        lastFourActivites.append("dream")
        
    elif timeElapsedSinceLastDream > 1800:
        #dream
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
        # dream
        dream()
        lastDreamTime = time.clock()
        del lastFourActivites[0]
        lastFourActivites.append("dream")

    return lastFourActivites, lastDreamTime

def reply_to_asks():
    # todo: move this into choose_activity and store as a var so that it isn't called twice
    #messageList = tumblr.get_messages()
    messageList = [("12345", "asker", "John has a beautiful voice")]
    if len(messageList) > 0:
        print "Fetched (" + str(len(messageList)) + ") new asks."
        for count, message in enumerate(messageList):
            # todo: intelligently decide how many asks to answer
            print "@" + message[1] + " >> " + message[2]
            # Consume message
            tokenizedMessage = parse.tokenize(message[2])
            consume(tokenizedMessage)
            
            reply = sentencebuilder.generate_sentence(tokenizedMessage)
            print "emma >> " + ' '.join(reply)
            tumblr.post_reply(message[1], message[2], reply)
    else:
        print "No new asks :("
        
reply_to_asks()     # todo: remove debug function call

def learn_new_words():
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_new = 1;')
        newWords = cursor.fetchall()
    if newWords:
        # todo: intelligently choose a number of words to learn
        for word in newWords:
            print "Learning more about \"%s\"..." % word
            word = str(word[0])
            results = tumblr.search_for_text_posts(word)
            for result in results:
                tokenizedResult = parse.tokenize(result)
                if tokenizedResult:
                    consume(tokenizedResult)
            with connection:
                cursor.execute("UPDATE dictionary SET is_new = 0 WHERE word = \'%s\';" % word)

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