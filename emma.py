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
import os
import pickle
import cgi

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
from config import debug, console, files, tumblr

class stack(list):
    def push(self, item):
        self.insert(0, item)
        self.remove(self[10])

connection = sql.connect(files['dbPath'])
cursor = connection.cursor()

print ("Checking for concept database at %s..." % files['dbPath']),
with connection:
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'associationmodel\';")
    if cursor.fetchone() == (u'associationmodel',): print Fore.GREEN + "[Done]"
    else:
        print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating new database...",
        cursor.executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS friends;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, is_new INTEGER DEFAULT 1, is_banned INTEGER DEFAULT 0);
        CREATE TABLE friends(username TEXT, can_reblog_from INTEGER DEFAULT 0);
        """)
        print Fore.GREEN + "[Done]"

print ("Checking for mood file at %s..." % files['moodPath']),
if os.path.isfile(files['moodPath']):
    print Fore.GREEN + "[Done]"
    with open(files['moodPath'],'r') as moodFile: moodHistory = stack(pickle.load(moodFile))
else:   
    print Fore.RED + "[File Not Found]\n" + Fore.YELLOW + "Creating file with randomized moods...",
    moodHistory = []
    with open(files['moodPath'],'wb') as moodFile:
        for i in range(0, 10): moodHistory.append(random.uniform(-0.5, 0.5))
        moodHistory = stack(moodHistory)
        pickle.dump(moodHistory, moodFile)
    print Fore.GREEN + "[Done]"

def update_mood(text):
    sentiment = pattern.en.sentiment(text)      # Get the average mood from the moods of sentences in the text
    moodHistory.push(sum(sentiment) / float(len(sentiment)))     # Add the mood to the list of mood values
    with open(files['moodPath'],'wb') as moodFile: pickle.dump(moodHistory, moodFile)        # Save to mood values file
    
    weightedmoodHistory = []
    for i in range(0, 3): weightedmoodHistory.append(moodHistory[0])
    for i in range(0, 2): weightedmoodHistory.append(moodHistory[1])
    weightedmoodHistory.append(moodHistory[2])

    weightedmoodHistory = weightedmoodHistory + moodHistory
    mood = sum(weightedmoodHistory) / float(len(weightedmoodHistory))
    
    if console['verboseLogging']: print "Mood values: %s\nCalculated mood: %d" % (str(moodHistory), mood)
    return mood

# "Emma" banner
print Fore.MAGENTA + u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' `88b `888P\"Y88bP\"Y88b  `888P\"Y88bP\"Y88b  `P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n`Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888\"\"8o\n\n·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.1\n"

with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print Fore.MAGENTA + "Database contains %s associations and %s words." % (associationModelItems, dictionaryItems)
    
def consume(parsedMessage, asker=u""):
    intents = []
    for count, parsedSentence in enumerate(parsedMessage):
        print "Consuming sentence %d of %d..." % (count + 1, len(parsedMessage))

        pronouns.determine_references(parsedSentence)
        pronouns.flip_posessive_references(parsedSentence, asker)
        intent = parse.determine_intent(parsedSentence)
        if intent['interrogative'] == False:
            parse.add_new_words(parsedSentence)
            associationtrainer.find_associations(parsedSentence)
        intents.append(intent)
        print "Sentence consumed."
    return intents

def express_mood(moodNum):
    if -0.8 > moodNum: moodStr = u"abysmal \ud83d\ude31"
    elif -0.6 > moodNum >= 0.8: moodStr = u"dreadful \ud83d\ude16"
    elif -0.4 > moodNum >= 0.6: moodStr = u"bad \ud83d\ude23"
    elif -0.2 > moodNum >= 0.4: moodStr = u"crummy \ud83d\ude41"
    elif 0.0 > moodNum >= -0.2: moodStr = u"blah \ud83d\ude15"
    elif 0.2 > moodNum >= 0.0: moodStr = u"alright \ud83d\ude10"
    elif 0.4 > moodNum >= 0.2: moodStr = u"good \ud83d\ude42"
    elif 0.6 > moodNum >= 0.4: moodStr = u"great \ud83d\ude09"
    elif 0.8 > moodNum >= 0.6: moodStr = u"fantastic \ud83d\ude00"
    elif 1.0 > moodNum >= 0.8: moodStr = u"glorious \ud83d\ude1c"
    return moodStr

def reply_to_asks(askList):
    if len(askList) > 0:
        print "Fetched %d new asks." % len(askList)
        for askCount, ask in enumerate(askList):
            print "Reading ask no. %d of %d..." % (askCount + 1, len(askList))
            print Fore.BLUE + u"@" + ask['asker'] + u" >> " + ask['message']

            friendsList = []
            with connection:
                cursor.execute("SELECT username FROM friends")
                for name in cursor.fetchall(): friendsList.append(name[0])
                if not ask['asker'] in friendsList: 
                    print Fore.BLUE + "Adding @%s to friends list..." % ask['asker']
                    cursor.execute("INSERT INTO friends(username) VALUES(\'%s\');" % ask['asker'])

            parsedAsk = parse.tokenize(ask['message'])
            intents = consume(parsedAsk, ask['asker'])
            understanding = utilities.pretty_print_understanding(parsedAsk, intents)
            reply = sentencebuilder.generate_sentence(parsedAsk, update_mood(ask['message']), intents, ask['asker'])

            if "%" not in reply:
                print Fore.BLUE + u"emma >> %s" % reply

                print "Posting reply..."
                print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "@" + ask['asker'] + ">> " + ask['message'] + "\n\n" + "emma >> " + reply + "\n\n"
                body = "<a href=" + ask['asker'] + ".tumblr.com/>@" + ask['asker'] + "</a>" + cgi.escape(" >> ") + cgi.escape(ask['message']) + "\n\n" + cgi.escape("emma >> ") + cgi.escape(reply) + "\n<!-- more -->\n" + cgi.escape(understanding)
                tumblrclient.post(body.encode('utf-8'), ["dialogue", ask['asker'].encode('utf-8'), "feeling " + express_mood(update_mood(reply)).encode('utf-8')])
            else:
                print Fore.YELLOW + "Reply generation failed."

            tumblrclient.delete_ask(ask['id'])

            if debug['enableSleep']:
                print "Sleeping for 3 minutes..."
                time.sleep(180)
            else:
                print Fore.YELLOW + "!!! Sleep disabled in config file -- execution will continue normally in 2 seconds..."
                time.sleep(2)

def reblog_post():
    with connection:
        cursor.execute("SELECT username FROM friends WHERE can_reblog_from = 1")
        SQLReturn = cursor.fetchall()
    posts = tumblrclient.get_recent_posts(random.choice(SQLReturn)[0])

    if len(posts) > 0:
        print "Found %d rebloggable posts." % len(posts)
        while posts:
            post = random.choice(posts)
            posts.remove(post)

            mood = express_mood(update_mood(post['body']))
            comment = sentencebuilder.generate_sentence(pattern.en.parse(post['body'], True, True, True, True, True).split(), mood)
            
            if "%" not in comment:
                print Fore.BLUE + u"Emma >> " + comment
                tumblrclient.reblog(post['id'], post['reblogKey'], comment.encode('utf-8'), ["reblog", post['blogName'].encode('utf-8'), "feeling " + mood.encode('utf-8')])
                break
            else: print Fore.YELLOW + "Reply generation failed."
    else: print Fore.YELLOW + "No rebloggable posts found."

def dream():
    with connection:
        cursor.execute('SELECT word FROM dictionary WHERE is_banned = 0 ORDER BY RANDOM() LIMIT 10;')
        SQLReturn = cursor.fetchall()
    dreamSeed = ""
    for word in SQLReturn:
        dreamSeed += word[0] + " "
    print "Dream seed: " + dreamSeed
    dream = sentencebuilder.generate_sentence(pattern.en.parse(dreamSeed, True, True, True, True, True).split(), update_mood(dreamSeed))
    if "%" not in dream:
        print Fore.BLUE + u"dream >> " + dream
        tumblrclient.post(cgi.escape(dream.encode('utf-8')), ["dreams", "feeling " + express_mood(update_mood(dream)).encode('utf-8')])
    else: print Fore.YELLOW + "Dreamless sleep..."

def chat():
    print Fore.YELLOW + "!!! Chat mode enabled in config file. Press Control-C to exit."
    while True:
        input = raw_input(Fore.BLUE + 'You >> ').decode('utf-8')
        tokenizedMessage = parse.tokenize(input)
        intents = consume(tokenizedMessage)
        
        reply = sentencebuilder.generate_sentence(tokenizedMessage, update_mood(input), intents)
        if "%" not in reply: print Fore.BLUE + u"emma >> " + reply
        else: print Fore.RED + u"Reply generation failed."

while True:
    if console['chatMode']: chat()
    else:
        print "Choosing activity..."
        if debug['fetchRealAsks']: askList = tumblrclient.get_asks()
        else: 
            print Fore.YELLOW + "!!! Real ask fetching disabled in config file. Using fake asks instead."
            askList = debug['fakeAsks']

        if askList != [] and debug['enableReplies']: 
            print "Replying to messages..."
            reply_to_asks(askList)
        else:
            activity = random.choice(['reblog', 'dream'])
            if activity == 'reblog' and debug['enableReblogs']:
                print "Reblogging a post..."
                reblog_post()
            if activity == 'dream' and debug['enableDreams']:
                print "Dreaming..."
                dream()
        
        if debug['enableSleep']:
            print "Sleeping for 10 minutes..."
            time.sleep(600)
        else:
            print Fore.YELLOW + "!!! Sleep disabled in config file -- execution will continue normally in 2 seconds..."
            time.sleep(2)