'''
Expanding Model of Mapped Associations
Copyright (C) 2016 Ellie Cochran & Alexander Howard

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# Name:             High-Level Emma Module
# Description:      Controls high-level functions and decision making
# Section:  
import time
import random
import pickle
import cgi
import re
import os

import pattern.en
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

def lpush(l, item):
    # Push item into the front of a list, pop out the last item in the list
    l.insert(0, item)
    l.remove(l[-1])

print "Loading database...",
if os.path.isfile('emma.db'): print Fore.GREEN + "[DONE]"
else:
    print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating new database...",
    with sql.connect('emma.db') as genConnection:       # This is done with a temporary connection because if the connection is initialized before this point, os.path.isfile() will find (the empty) emma.db
        genConnection.cursor().executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS friends;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, synonyms TEXT, affinity DOUBLE DEFAULT 0, is_banned INTEGER DEFAULT 0);
        CREATE TABLE friends(username TEXT);
        """)
    print Fore.GREEN + "[DONE]"

print "Loading mood history...",
if os.path.isfile('moodHistory.p'):
    print Fore.GREEN + "[DONE]"
    with open('moodHistory.p','r') as moodFile: moodHistory = pickle.load(moodFile)
else:   
    print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating file...",
    with open('moodHistory.p','wb') as moodFile:
        moodHistory = [0] * 10
        pickle.dump(moodHistory, moodFile)
    print Fore.GREEN + "[DONE]"

# "Emma" banner
print Fore.MAGENTA + u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' \u006088b \u0060888P\"Y88bP\"Y88b  \u0060888P\"Y88bP\"Y88b  \u0060P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n\u0060Y8bod8P' o888o o888o o888o o888o o888o o888o \u0060Y888\"\"8o\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.4\n"

connection = sql.connect('emma.db')
cursor = connection.cursor()
with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print Fore.MAGENTA + "Database contains %s associations for %s words." % (associationModelItems, dictionaryItems)

import questionparser
import pronouns
import parse
import associationtrainer
import replybuilder
import utilities

def get_mood(update=False, text="", expressAsText=True):
    global moodHistory
    # If update is set to true, use text to add new mood value. Otherwise, just return the mood without touching it
    # By default, this function does nothing and just returns Emma's mood in human-readable form (as opposed to numbers)
    if update: 
        sentiment = pattern.en.sentiment(text)       # Get the average mood from the moods of sentences in the text
        lpush(moodHistory, (sum(sentiment) / float(len(sentiment))))        # Add the mood to the list of mood values
        with open('moodHistory.p','wb') as moodFile: pickle.dump(moodHistory, moodFile)       # Save to mood values file
    else: 
        with open('moodHistory.p', 'r') as moodFile: moodHistory = pickle.load(moodFile)

    # More recent mood values have a higher weight when calculating Emma's overall mood
    weightedmoodHistory = [moodHistory[0]]*3 + [moodHistory[1]]*2 + moodHistory[2:]
    mood = sum(weightedmoodHistory) / float(len(weightedmoodHistory))

    if not expressAsText: return mood
    else:
        if -0.8 > mood: moodStr = u"abysmal \ud83d\ude31"
        elif -0.6 > mood >= -0.8: moodStr = u"dreadful \ud83d\ude16"
        elif -0.4 > mood >= -0.6: moodStr = u"bad \ud83d\ude23"
        elif -0.2 > mood >= -0.4: moodStr = u"crummy \ud83d\ude41"
        elif 0.0 > mood >= -0.2: moodStr = u"blah \ud83d\ude15"
        elif 0.2 > mood >= 0.0: moodStr = u"alright \ud83d\ude10"
        elif 0.4 > mood >= 0.2: moodStr = u"good \ud83d\ude42"
        elif 0.6 > mood >= 0.4: moodStr = u"great \ud83d\ude09"
        elif 0.8 > mood >= 0.6: moodStr = u"fantastic \ud83d\ude00"
        elif mood >= 0.8: moodStr = u"glorious \ud83d\ude1c"
        return u"feeling " + moodStr
    
def consume(parsedMessage, sender=u""):
    intents = []
    questionPackages = []

    pronouns.determine_references(parsedMessage)

    for count, parsedSentence in enumerate(parsedMessage):
        print "Consuming sentence " + str(count + 1) + " of " + str(len(parsedMessage)) + "..."

        pronouns.determine_posessive_references(parsedSentence, sender)
        intent = parse.determine_intent(parsedSentence)

        # If the sentence is interrogative, package it and add the package to questionPackages
        if intent['interrogative']:
            questionPackage = questionparser.read_question(parsedSentence)
            if questionPackage != None: questionPackages.append(questionparser.read_question(parsedSentence))
        else:
            parse.add_new_words(parsedSentence)
            associationtrainer.find_associations(parsedSentence)
        intents.append(intent)
    return intents, questionPackages

def input(message, sender=u"you"):
    tokenizedMessage = parse.tokenize(message.decode('utf-8'))
    intents, questionPackages = consume(tokenizedMessage, sender)
    
    reply = replybuilder.generate_sentence(tokenizedMessage, get_mood(update=True, text=input, expressAsText=False), intents, questionPackages=questionPackages)
    if "%" not in reply: 
        print Fore.BLUE + u"Emma >> " + reply
        return reply
    else: 
        print Fore.RED + "Reply generation failed."
        return "%"