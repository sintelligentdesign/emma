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

print "Checking for concept database and mood values..."
if console['verboseLogging']: print "Checking for concept database at %s..." % files['dbPath']
with connection:
    cursor.execute("SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'associationmodel\';")
    if cursor.fetchone() == (u'associationmodel',): print Fore.GREEN + "Database found!"
    else:
        print Fore.YELLOW + "Concept database not found. Creating database at %s..." % files['dbPath']
        cursor.executescript("""
        DROP TABLE IF EXISTS associationmodel;
        DROP TABLE IF EXISTS dictionary;
        DROP TABLE IF EXISTS friends;
        CREATE TABLE associationmodel(word TEXT, association_type TEXT, target TEXT, weight DOUBLE);
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, is_new INTEGER DEFAULT 1, is_banned INTEGER DEFAULT 0);
        CREATE TABLE friends(username TEXT, can_reblog_from INTEGER DEFAULT 0);
        """)

if console['verboseLogging']: print "Checking if mood values file exists at %s..." % files['moodPath']
if os.path.isfile(files['moodPath']):
    print Fore.GREEN + "Mood values file found! Loading values..."
    with open(files['moodPath'],'r') as moodFile: moodValues = stack(pickle.load(moodFile))
else:   
    print Fore.YELLOW + "Mood values file not found! Creating file with randomized moods at %s..." % files['moodPath']
    moodValues = []
    with open(files['moodPath'],'wb') as moodFile:
        for i in range(0, 10): moodValues.append(random.uniform(-0.5, 0.5))
        moodValues = stack(moodValues)
        pickle.dump(moodValues, moodFile)

def update_mood(text):
    sentiment = pattern.en.sentiment(text)      # Get the average mood from the moods of sentences in the text
    moodValues.push(sum(sentiment) / float(len(sentiment)))     # Add the mood to the list of mood values
    with open(files['moodPath'],'wb') as moodFile: pickle.dump(moodValues, moodFile)        # Save to mood values file
    
    weightedMoodValues = []
    for i in range(0, 3): weightedMoodValues.append(moodValues[0])
    for i in range(0, 2): weightedMoodValues.append(moodValues[1])
    weightedMoodValues.append(moodValues[2])

    weightedMoodValues = weightedMoodValues + moodValues
    mood = sum(weightedMoodValues) / float(len(weightedMoodValues))
    
    if console['verboseLogging']: print "Mood values: %s\nCalculated mood: %d" % (str(moodValues), mood)
    return mood

# "Emma" banner
print Fore.MAGENTA + u" .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' `88b `888P\"Y88bP\"Y88b  `888P\"Y88bP\"Y88b  `P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n`Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888\"\"8o\n\n·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.1"
    
def consume(parsedSentence, asker=u""):
    if console['verboseLogging']: print "Consuming sentence..."
    pronouns.determine_references(parsedSentence)
    pronouns.flip_posessive_references(parsedSentence, asker)
    parse.add_new_words(parsedSentence)
    associationtrainer.find_associations(parsedSentence)
    intent, details = parse.determine_intent(parsedSentence)
    if console['verboseLogging']: print "Sentence consumed."
    return intent, details


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

            understanding = u""
            intents = []
            for sentenceCount, sentence in enumerate(parsedAsk):
                if console['verboseLogging']: print "Reading sentence no. %d of ask no. %d..." % ((sentenceCount + 1), (askCount + 1))
                intent, details = consume(sentence, ask['asker'])
                intents.append(intent)
            
                for wordCount, word in enumerate(sentence):
                    if wordCount == 0 and sentenceCount != 0:
                        understanding += u" "
                    understanding += word[0]
                    if wordCount < len(sentence) - 2:
                        understanding += u" "
            understanding = u"Emma interpreted this message as: \'%s\' %s" % (understanding, str(intents))
            print Fore.BLUE + understanding

            print Fore.BLUE + "Intents: " + str(intents)
            reply = sentencebuilder.generate_sentence(parsedAsk, update_mood(ask['message']), intents, intentDetails, ask['asker'])

            if "%" not in reply:
                print Fore.BLUE + u"emma >> %s" % reply

                print "Posting reply..."
                body = "@%s >> %s\n(%s)\n\nemma >> %s" % (ask['asker'], ask['message'], understanding, reply)
                tumblrclient.post(body.encode('utf-8'), ["dialogue", ask['asker'].encode('utf-8'), "feeling " + express_mood(update_mood(reply)).encode('utf-8')])
            else:
                print Fore.YELLOW + "Sentence generation failed."

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

    while posts:
        post = random.choice(posts)
        posts.remove(post)
        print "Attempting to reply to @%s\'s post (attempt %d of 5)..." % (post['blogName'], 5 - len(posts))
        comment = sentencebuilder.generate_sentence(pattern.en.parse(post['body'], True, True, True, True, True).split(), mood)
        
        if "%" not in comment:
            print Fore.BLUE + u"Emma >> " + comment
            tumblrclient.reblog(post['id'], post['reblogKey'], comment.encode('utf-8'), ["reblog", post['blogName'].encode('utf-8'), "feeling " + express_mood(update_mood(post['body'])).encode('utf-8')])
            break
        else: print Fore.YELLOW + "Reply generation failed."

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
        tumblrclient.post(dream.encode('utf-8'), ["dreams", "feeling " + express_mood(update_mood(dream)).encode('utf-8')])
    else: print Fore.YELLOW + "Dreamless sleep..."

def chat():
    print Fore.YELLOW + "!!! Chat mode enabled in config file. Press Control-C to exit."
    while True:
        input = raw_input(Fore.BLUE + 'You >> ').decode('utf-8')
        tokenizedMessage = parse.tokenize(input)
        intents = []
        for sentence in tokenizedMessage: intents.append(consume(sentence))
        
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