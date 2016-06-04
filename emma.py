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
    bias = random.choice(activities)
    
    # todo: do math to this to decide what emma wants to do
    
def reply_to_asks():
    testInput = ["I made a pretty whistle out of wood.", "It sounds good.", "I'm back.", "He ate an apple.", "His friend watched longingly."]
    for sentence in testSet:
        markovtrainer.train(tokenize(sentence))
        add_new_words(tokenize(sentence))

    
while True:
    main()
    print "Sleeping for 10 seconds..."
    time.sleep(10)