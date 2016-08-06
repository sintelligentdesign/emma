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

connection = sql.connect('emma.db')
cursor = connection.cursor()

print "Loading database...",
if os.path.isfile('emma.db'):
    print Fore.GREEN + "[DONE]"
else:
    print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating new database...",
    with connection:
        cursor.executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS contacts;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, synonyms TEXT, affinity DOUBLE DEFAULT 0, is_banned INTEGER DEFAULT 0);
        CREATE TABLE contacts(username TEXT, is_friend INTEGER DEFAULT 0, is_banned INTEGER DEFAULT 0);
        """)
    print Fore.GREEN + "[DONE]"

print "Loading mood history...",
if os.path.isfile('moodHistory.p'):
    print Fore.GREEN + "[Done]"
    with open('moodHistory.p','r') as moodFile: moodHistory = pickle.load(moodFile)
else:   
    print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating file...",
    with open('moodHistory.p','wb') as moodFile:
        moodHistory = [0] * 10
        pickle.dump(moodHistory, moodFile)
    print Fore.GREEN + "[Done]"

# "Emma" banner
print Fore.MAGENTA + u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' \u006088b \u0060888P\"Y88bP\"Y88b  \u0060888P\"Y88bP\"Y88b  \u0060P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n\u0060Y8bod8P' o888o o888o o888o o888o o888o o888o \u0060Y888\"\"8o\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.3\n"

with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print Fore.MAGENTA + "Database contains %s associations for %s words." % (associationModelItems, dictionaryItems)

import tumblrclient
import questionparser
import pronouns
import parse
import associationtrainer
import sentencebuilder
import utilities
import settings

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
    if settings.option('general', 'verboseLogging'): print Fore.MAGENTA + "Mood values: %s\nCalculated mood: %s" % (str(moodHistory), str(mood))

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
    
def consume(parsedMessage, asker=u""):
    intents = []
    questionPackages = []

    pronouns.determine_references(parsedMessage)

    for count, parsedSentence in enumerate(parsedMessage):
        print "Consuming sentence %d of %d..." % (count + 1, len(parsedMessage))

        pronouns.determine_posessive_references(parsedSentence, asker)
        intent = parse.determine_intent(parsedSentence)
        if settings.option('general', 'verboseLogging'): print intent       # todo: delete debug print statement

        # If the sentence is interrogative, package it and add the package to questionPackages
        if intent['interrogative']:
            questionPackage = questionparser.read_question(parsedSentence)
            if questionPackage != None: questionPackages.append(questionparser.read_question(parsedSentence))
        else:
            parse.add_new_words(parsedSentence)
            associationtrainer.find_associations(parsedSentence)
        intents.append(intent)
        print "Sentence consumed."
    return intents, questionPackages

def reply_to_ask(ask):
    print "Reading ask..."
    print Fore.BLUE + u"@" + ask['asker'] + u" >> " + ask['message']

    parsedAsk = parse.tokenize(ask['message'])
    intents, questionPackages = consume(parsedAsk, ask['asker'])
    understanding = utilities.pretty_print_understanding(parsedAsk, intents)

    reply = sentencebuilder.generate_sentence(parsedAsk, get_mood(update=True, text=ask['message'], expressAsText=False), intents, ask['asker'], questionPackages)

    if "%" not in reply:
        print Fore.BLUE + u"emma >> %s" % reply
        print "Posting reply..."
        if settings.option('tumblr', 'enablePostPreview'): print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "@" + ask['asker'] + " >> " + ask['message'] + "\n\n" + "emma >> " + reply + "\n- - - - - - - - - - -\n" + get_mood(update=False, expressAsText=True) + "\n\n"
        answer = cgi.escape(reply) + "\n<!-- more -->\n" + cgi.escape(understanding)
        tumblrclient.post_ask(ask['id'], answer.encode('utf-8'), ["dialogue", ask['asker'].encode('utf-8'), get_mood().encode('utf-8')])
    else: print Fore.RED + "Reply generation failed."

    tumblrclient.delete_ask(ask['id'])

def reblog_post():
    with connection:
        cursor.execute("SELECT username FROM contacts WHERE is_friend = 1;")
        SQLReturn = cursor.fetchall()
    posts = tumblrclient.get_recent_posts(random.choice(SQLReturn)[0])

    if len(posts) > 0:
        print "Found %d rebloggable posts." % len(posts)
        while posts:
            post = random.choice(posts)
            posts.remove(post)

            mood = get_mood(update=True, text=post['body'])
            comment = sentencebuilder.generate_sentence(pattern.en.parse(post['body'], True, True, True, True, True).split(), mood)
            
            if "%" not in comment:
                print Fore.BLUE + u"Emma >> " + comment
                tumblrclient.reblog(post['id'], post['reblogKey'], comment.encode('utf-8'), ["reblog", post['blogName'].encode('utf-8'), mood.encode('utf-8')])
                break
            else: print Fore.RED + "Reply generation failed."
    else: print Fore.RED + "No rebloggable posts found."

def dream():
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_banned = 0 ORDER BY RANDOM() LIMIT 10;')
        SQLReturn = cursor.fetchall()

    print Fore.GREEN + "Creating common sense halo..."
    halo = []
    with connection:
        cursor.execute("SELECT target FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.target = dictionary.word WHERE associationmodel.word = \"%s\" AND part_of_speech IN (\'NN\', \'NNS\', \'NNP\', \'NNPS\');" % re.escape(random.choice(SQLReturn)[0]))
        for fetchedWord in cursor.fetchall():
            if fetchedWord[0] not in halo: halo.append(fetchedWord[0])
            
    dream = sentencebuilder.generate_sentence(pattern.en.parse(' '.join(halo), True, True, True, True, True).split(), get_mood(expressAsText=False))
    if "%" not in dream:
        print Fore.BLUE + u"emma >> " + dream
        tumblrclient.post_text(cgi.escape(dream.encode('utf-8')), ["dreams", get_mood(update=True, text=dream).encode('utf-8')])
    else: print Fore.RED + "Dreamless sleep..."

def chat():
    input = raw_input(Fore.BLUE + 'You >> ').decode('utf-8')
    tokenizedMessage = parse.tokenize(input)
    intents, questionPackages = consume(tokenizedMessage)
    
    reply = sentencebuilder.generate_sentence(tokenizedMessage, get_mood(update=True, text=input, expressAsText=False), intents, questionPackages=questionPackages)
    if "%" not in reply: print Fore.BLUE + u"emma >> " + reply
    else: print Fore.RED + u"Reply generation failed."