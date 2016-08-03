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

import random
import json
import time
import argparse

from colorama import init, Fore
init(autoreset = True)
from GUI import Window, Label, CheckBox, Button, application
from GUI.StdColors import grey

import settings
import emma
import tumblrclient
import utilities

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

        if len(activities) > 0: activity = random.choice(activities)
        else: print Fore.RED + "No available activities. Double-check the Settings panel."

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

    if option == "enableAskReplies":        # This gets a special section because it toggles visibility of other checkboxes
        if enableAskRepliesBox.on:
            enableAskDeletionBox.container = win
            fetchRealAsksBox.container = win
        else:
            enableAskDeletionBox.container = None
            fetchRealAsksBox.container = None
    
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