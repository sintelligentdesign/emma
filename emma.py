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
    messageList = tumblr.get_messages()
    print "Fetched (" + str(len(messageList)) + ") new asks."       # todo: if there are no new asks, quit
    for count, message in enumerate(messageList):
        # todo: intelligently decide how many asks to answer
        currentMessage = message        # so that other functions can reference information from the message
        # Consume message
        # todo: print message to console
        tokenizedMessage = parse.tokenize(message[2])
        consume(tokenizedMessage)
        
        # Reply to message
        # todo: shorten this to one line
        print "Creating reply..."
        reply = sentencelayoutgen.generate()
        reply = chunkunpacker.unpack(reply)
        # todo: fill parts of speech with words
        #       move sentence generation to its own function
        print "emma >> " + ' '.join(reply)
        tumblr.post_reply(message[1], message[2], reply)
        
def consume(sentence):
    parse.add_new_words(sentence)
    markovtrainer.train(sentence)
    print "Sentence consumed."
    
#while True:
#    main()
#    print "Sleeping for 10 seconds..."
#    time.sleep(10)

reply_to_asks()