# -*- coding: utf-8 -*-
# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          LEARNING, REPLY
import time

import pytumblr
import pattern.web
from colorama import init, Fore
init(autoreset = True)

import apikeys
from config import tumblr

# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.tumblrConsumerKey,
    apikeys.tumblrConsumerSecret,
    apikeys.tumblrOauthToken,
    apikeys.tumblrOauthSecret
)

def get_messages():
    print "Checking Tumblr messages..."
    asks = client.submission(tumblr['username'] + '.tumblr.com')
    asks = asks.values()        # unwrap JSON
    asks = asks[0]

    messageList = []
    for ask in asks: messageList.append((ask['id'], ask['asking_name'], ask['question']))
    return messageList

def delete_ask(askid):
    if tumblr['enableAskDeletion']: 
        print "Deleting ask with ID %s..." % askid
        client.delete_post(tumblr['username'], askid)
    else: print Fore.YELLOW + "!!! Ask deletion disabled in config file."

def post_reply(asker, question, understanding, reply, mood):
    body = "@%s >> %s\n(%s)\n\nemma >> %s" % (asker, question, understanding, reply)
    body = body.encode('utf-8')
    tags = ["dialogue", asker, "mood: " + mood]
    if tumblr['enablePostPreview']: preview_post(body, tags)
    if tumblr['enablePosting']: client.create_text(tumblr['username'], state="published", body=body, tags=tags)
    else: print Fore.YELLOW + "!!! Posting disabled in config file."

def post_dream(dream):
    body = dream.encode('utf-8')
    tags = ["dreams"]
    if tumblr['enablePostPreview']: preview_post(body, tags)
    if tumblr['enablePosting']: client.create_text(tumblr['username'], state="published", body=body, tags=tags)
    else: print Fore.YELLOW + "!!! Posting disabled in config file."

def preview_post(body, tags):
    for count, tag in enumerate(tags):
        tags[count] = "#" + tag
    tags = ' '.join(tags)
    print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n" 
    print body
    print "- - - - - - - - - - - - - - - - - - - - - - - - -"
    print tags + "\n\n"