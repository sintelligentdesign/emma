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
import sentencelayoutgen
import chunkunpacker

lastDreamTime = time.clock()

connection = sql.connect('emma.db')
cursor = connection.cursor()

def main():
    chooseActivity()
    
def choose_activity():
    # get number of new words
    with connection:
        cursor.execute('SELECT * FROM dictionary WHERE is_new = 1')
        newWords = len(cursor.fetchall())
    
    # get number of new tumblr asks
    newAsks = len(tumblr.get_messages())
    
    # get time elapsed since last dream period
    timeElapsedSinceLastDream = time.clock() - lastDreamTime
    
    # get bias
    activities = ["tumblr", "learn words", "dream"]
    
    # todo: do math to this to decide what emma wants to do
    
def reply_to_asks():
    testInput = ["I made a pretty whistle out of wood.", "It sounds good.", "I'm back.", "He ate an apple.", "His friend watched longingly."]
    print "Fetching asks from Tumblr..."
    # todo: move this into choose_activity and store as a var so that it isn't called twice
    messageList = tumblr.get_messages()
    if len(messageList) > 0:
        print "Fetched (" + str(len(messageList)) + ") new asks."
        for count, message in enumerate(messageList):
            # todo: intelligently decide how many asks to answer
            print "@" + message[1] + " >> " + message[2]
            # Consume message
            tokenizedMessage = parse.tokenize(message[2])
            consume(tokenizedMessage)
            
            # Reply to message
            print "Creating reply..."
            reply = chunkunpacker.unpack(
                sentencelayoutgen.generate()
                )
            # todo: fill parts of speech with words
            #       move sentence generation to its own function
            print "emma >> " + ' '.join(reply)
            tumblr.post_reply(message[1], message[2], reply)
    else:
        print "No new asks :("
        
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
        
def consume(sentence):
    parse.add_new_words(sentence)
    markovtrainer.train(sentence)
    print "Sentence consumed."
    
#while True:
#    main()
#    print "Sleeping for 10 seconds..."
#    time.sleep(10)

reply_to_asks()