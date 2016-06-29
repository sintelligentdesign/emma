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

def post(body, tags=[]):
    if tumblr['enablePostPreview']: 
        for count, tag in enumerate(tags): tags[count] = u"#" + tag
        tags = u' '.join(tags)
        print Fore.BLUE + u"\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + u"%s\n- - - - - - - - - - - - - - - - - - - - - - - - -\n%s\n\n" % (body.encode('utf-8'), tags)
    if tumblr['enablePosting']: client.create_text(tumblr['username'], state="published", body=body, tags=tags)
    else: print Fore.YELLOW + "!!! Posting disabled in config file."