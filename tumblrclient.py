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

    messageList = []
    for ask in asks.values()[0]: messageList.append((int(ask['id']), ask['asking_name'], ask['question']))
    return messageList

def get_recent_posts(user):
    print "Fetching @%s\'s 5 most recent text posts..." % user
    posts = client.posts(user + '.tumblr.com', type='text', limit=5, filter='text')[u'posts']
    
    postList = []
    for post in posts: 
        body = post['body'].split(' ')
        for count, word in enumerate(body):
            if u':' in word or word == u"" or len(word) > 10: leftBound = count + 1
            else:
                body = ' '.join(body[leftBound:])
                break
        postList.append((int(post['id']), post['reblog_key'], post['blog_name'], body))
    return postList

def delete_ask(askid):
    if tumblr['enableAskDeletion']: 
        print "Deleting ask with ID %d..." % askid
        client.delete_post(tumblr['username'], askid)
    else: print Fore.YELLOW + "!!! Ask deletion disabled in config file."

def post(body, tags=[]):
    if tumblr['enablePostPreview']: 
        tagsAsString = ""
        for tag in tags: tagsAsString += "#%s " % tag
        print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "%s\n- - - - - - - - - - - - - - - - - - - - - - - - -\n%s\n\n" % (body, tagsAsString)
    if tumblr['enablePosting']: client.create_text(tumblr['username'], state="published", body=body, tags=tags)
    else: print Fore.YELLOW + "!!! Posting disabled in config file."