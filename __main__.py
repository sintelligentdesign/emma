import os
import random
import pickle
import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

connection = sql.connect('emma.db')
cursor = connection.cursor()

print "Loading concept database...",
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
        CREATE TABLE dictionary(word TEXT, part_of_speech TEXT, synonyms TEXT, is_new INTEGER DEFAULT 1, is_banned INTEGER DEFAULT 0);
        CREATE TABLE friends(username TEXT, can_reblog_from INTEGER DEFAULT 0);
        """)
        print Fore.GREEN + "[Done]"

import json
import time
import random
import argparse

from GUI import Window, Label, CheckBox, Button, application
from GUI.StdColors import grey

import settings
import emma
import tumblrclient
import utilities

# "Emma" banner
print Fore.MAGENTA + u"\n .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.\nd88' \u006088b \u0060888P\"Y88bP\"Y88b  \u0060888P\"Y88bP\"Y88b  \u0060P  )88b\n888ooo888  888   888   888   888   888   888   .oP\"888\n888    .,  888   888   888   888   888   888  d8(  888\n\u0060Y8bod8P' o888o o888o o888o o888o o888o o888o \u0060Y888\"\"8o\n\n        EXPANDING MODEL of MAPPED ASSOCIATIONS\n                     Alpha v0.0.3\n"

with connection:
    cursor.execute("SELECT * FROM associationmodel")
    associationModelItems = "{:,d}".format(len(cursor.fetchall()))
    cursor.execute("SELECT * FROM dictionary")
    dictionaryItems = "{:,d}".format(len(cursor.fetchall()))
print Fore.MAGENTA + "Database contains %s associations and %s words." % (associationModelItems, dictionaryItems)

settingsList = settings.load_settings()

def run_emma():
    # If we aren't in chat mode, every 15 minutes, try to make a post. Replying to asks is most likely, followed by dreams, and reblogging a post is the least likely
    if settings.option('general', 'enableChatMode'): emma.chat()
    else:
        if settings.option('tumblr', 'fetchRealAsks'): askList = tumblrclient.get_asks()
        else: askList = utilities.fakeAsks

        print "Choosing activity..."
        activities = []
        if settings.option('tumblr', 'enableReblogs'): activities.append('reblogPost')
        if settings.option('tumblr', 'enableDreams'): activities.extend(['dream'] * 2)
        if settings.option('tumblr', 'enableAskReplies') and askList != []: activities.extend(['replyToAsks'] * 3)

        activity = random.choice(activities)
        if activity == 'reblogPost':
            print "Reblogging a post..."
            emma.reblog_post()
        elif activity == 'dream':
            print "Dreaming..."
            emma.dream()
        elif activity == 'replyToAsks':
            print "Fetched %d new asks. Responding the newest one..." % len(askList)
            # todo: maybe have Emma figure out if she's able to respond to an ask before calling reply_to_asks()?
            emma.reply_to_ask(askList[0])
        
        if settings.option('general', 'enableSleep'):
            print "Sleeping for 15 minutes..."
            time.sleep(900)

def loop_emma():
    win.hide()
    while True: run_emma()

# Emma GUI-related functions
def make_label(text, **kwds): return Label(text=text, **kwds)
def update_setting(option):
    settingsList = settings.load_settings()
    generalCheckboxMap = {'enableChatMode': enableChatModeBox.on, 'enableSleep': enableSleepBox.on, 'verboseLogging': verboseLoggingBox.on}
    tumblrCheckboxMap = {'publishOutput': publishOutputBox.on, 'enablePostPreview': enablePostPreviewBox.on, 'enableAskReplies': enableAskRepliesBox.on, 'enableAskDeletion': enableAskDeletionBox.on, 'fetchRealAsks': fetchRealAsksBox.on, 'enableReblogs': enableReblogsBox.on, 'enableDreams': enableDreamsBox.on}

    if option in generalCheckboxMap.keys():
        group = 'general'
        value = generalCheckboxMap[option]
    elif option in tumblrCheckboxMap.keys():
        group = 'tumblr'
        value = tumblrCheckboxMap[option]

    settingsList[group][option] = value
    with open('settings.json', 'w') as settingsFile: json.dump(settingsList, settingsFile)
    
parser = argparse.ArgumentParser(description='Entry point for Expanding Model of Mapped Associations.')
parser.add_argument('-gui', help='Show or hide Emma\'s GUI. If hidden, execution will begin automatically.', choices=['show', 'hide'], default='show')
args = parser.parse_args()
if args.gui == 'hide': 
    win = Window()
    loop_emma()

## Set up and display Emma's GUI
# General
generalLabel = make_label("General", color=grey, x=20, y=15)
enableChatModeBox = CheckBox(x=20, y=generalLabel.bottom, title="Chat mode", action=(update_setting, 'enableChatMode'))
enableSleepBox = CheckBox(x=20, y=enableChatModeBox.bottom, title="Enable sleep", action=(update_setting, 'enableSleep'))
verboseLoggingBox = CheckBox(x=20, y=enableSleepBox.bottom, title="Verbose Logging", action=(update_setting, 'verboseLogging'))

# Tumblr
tumblrLabel = make_label("Tumblr", color=grey, x=20, y=verboseLoggingBox.bottom+15)
publishOutputBox = CheckBox(x=20, y=tumblrLabel.bottom, title="Publish output", action=(update_setting, 'publishOutput'))
enablePostPreviewBox = CheckBox(x=20, y=publishOutputBox.bottom, title="Show post preview", action=(update_setting, 'enablePostPreview'))
enableAskRepliesBox = CheckBox(x=20, y=enablePostPreviewBox.bottom + 10, title="Enable Ask replies", action=(update_setting, 'enableAskReplies'))
enableAskDeletionBox = CheckBox(x=20, y=enableAskRepliesBox.bottom, title="Enable Ask deletion", action=(update_setting, 'enableAskDeletion'))
fetchRealAsksBox = CheckBox(x=20, y=enableAskDeletionBox.bottom, title="Fetch real Asks", action=(update_setting, 'fetchRealAsks'))
enableReblogsBox = CheckBox(x=20, y=fetchRealAsksBox.bottom + 10, title="Enable Reblogs", action=(update_setting, 'enableReblogs'))
enableDreamsBox = CheckBox(x=20, y=enableReblogsBox.bottom, title="Enable dreams", action=(update_setting, 'enableDreams'))

if settings.option('general', 'enableChatMode'): enableChatModeBox.on = True
if settings.option('general', 'enableSleep'): enableSleepBox.on = True
if settings.option('general', 'verboseLogging'): verboseLoggingBox.on = True
if settings.option('tumblr', 'publishOutput'): publishOutputBox.on = True
if settings.option('tumblr', 'enablePostPreview'): enablePostPreviewBox.on = True
if settings.option('tumblr', 'enableAskReplies'): enableAskRepliesBox.on = True
if settings.option('tumblr', 'enableAskDeletion'): enableAskDeletionBox.on = True
if settings.option('tumblr', 'fetchRealAsks'): fetchRealAsksBox.on = True
if settings.option('tumblr', 'enableReblogs'): enableReblogsBox.on = True
if settings.option('tumblr', 'enableDreams'): enableDreamsBox.on = True

loopButton = Button(x=15, y=enableDreamsBox.bottom + 15, width=170, title="Start Emma Loop", style='default', action=loop_emma)
runOnceButton = Button(x=15, y=loopButton.bottom + 5, width=170, title="Run Emma Once", style='normal', action=run_emma)

win = Window(width=200, height=runOnceButton.bottom + 20, title="Emma", auto_position=True, resizable=False, zoomable=False)

win.add(generalLabel)
win.add(enableChatModeBox)
win.add(enableSleepBox)
win.add(verboseLoggingBox)

win.add(tumblrLabel)
win.add(publishOutputBox)
win.add(enablePostPreviewBox)
win.add(enableAskRepliesBox)
win.add(enableAskDeletionBox)
win.add(fetchRealAsksBox)
win.add(enableReblogsBox)
win.add(enableDreamsBox)

win.add(loopButton)
win.add(runOnceButton)

win.show()
application().run()