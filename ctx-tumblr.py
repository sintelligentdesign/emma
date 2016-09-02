import pytumblr
import cgi
import re

import sqlite3 as sql
from colorama import init, Fore
init(autoreset = True)

import emma
import apikeys

connection = sql.connect('emma.db')
cursor = connection.cursor()

## Tumblr client functions
# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.tumblrConsumerKey,
    apikeys.tumblrConsumerSecret,
    apikeys.tumblrOauthToken,
    apikeys.tumblrOauthSecret
)

def client_get_asks():
    print "Checking Tumblr messages..."
    submissions = client.submission('emmacanlearn')     # todo: fix bug in which calling get_asks() more than once results in a 401 Unauthorized error
    askList = []
    if 'posts' in submissions.keys():       # temporary bugfix for above
        for submission in submissions['posts']: askList.append({'id': submission['id'], 'asker': submission['asking_name'], 'message': submission['question']})
    return askList

def client_get_rebloggable_posts(user):
    posts = client.posts(user, type='text', filter='text')[u'posts']

    postList = []
    for post in posts:
        # Only allow posts that were posted by the blog owner and are also under 800 characters...
        if u'is_root_item' in post['trail'][0].keys() and len(post['trail']) < 2 and len(post['body']) < 800:
            # ...But don't allow posts with tags in the realm of 'personal' or 'do not reblog'
            taggedDoNotReblog = False
            for tag in post['tags']:
                if re.sub(r'[\d\s\W]', "", tag.lower()) in [u"personal", u"donotreblog", u"dontreblog", u"dontrb", u"nsfw" u"epilepsywarning"]: taggedDoNotReblog = True
                elif re.sub(r'\d\W', " ", tag.lower()).startswith((u"trigger warning ", u"content warning ", u"tw ", u"cw")) or re.sub(r'\d\W', " ", tag.lower()).endswith((u" trigger warning", u" content warning", u" tw", u" cw")): taggedDoNotReblog = True
            if not taggedDoNotReblog: postList.append({'id': int(post['id']), 'reblogKey': post['reblog_key'], 'blogName': cgi.escape(post['blog_name']), 'body': post['body']})
    return postList

def client_post_text(body, tags=[]): client.create_text('emmacanlearn', state="published", body=body, tags=tags)

def client_answer_ask(id, answer, tags=[]): 
    client.edit_post('emmacanlearn', id=id, answer=answer, state='published', tags=tags, type='answer')
    client.delete_post('emmacanlearn', id)

def client_reblog(postid, reblogKey, comment, tags):
    print "Reblogging post & adding comment..."
    client.reblog('emmacanlearn', id=postid, reblog_key=reblogKey, comment=cgi.escape(comment), tags=tags)

## Actions
def reblog_post():
    print "Fetching friends list..."
    friendsList = []
    with connection:
        cursor.execute("SELECT username FROM friends;")
        for row in cursor.fetchall(): friendsList.append(row[0])

    random.shuffle(friendsList)

    for friend in friendsList:
        print "Checking @%s's blog for rebloggable posts..." % friend
        posts = client_get_rebloggable_posts(friend)
        if len(posts) != 0:
            print "Attempting to create a reply to @%s\'s post..." % friend
            post = random.choice(posts)

            comment = emma.input(post['body'], friend)
            if comment != "%":
                client_reblog(post['id'], post['reblogKey'], comment.encode('utf-8'), ["reblog", post['blogName'].encode('utf-8'), mood.encode('utf-8')])
                return
            else: print Fore.RED + "Reply generation failed."
        else: print Fore.RED + "No posts found."
    print Fore.RED + "No rebloggable posts."

def dream():
    for i in range(0, 4):       # 5 attempts to generate a dream
        print "Attempting to dream (attempt %s of 5)." % i
        with connection:
            # Get seed word
            cursor.execute('SELECT word FROM dictionary WHERE is_banned = 0 ORDER BY RANDOM() LIMIT 1;')
            seed = cursor.fetchone()[0]

        dream = emma.input(seed)
        if dream != "%":
            client_post_text(cgi.escape(dream.encode('utf-8')), ["dreams", get_mood(update=True, text=dream).encode('utf-8')])
            return
        else: print Fore.RED + "Generation failed."
    print Fore.RED + "Dreamless sleep."

def reply_to_ask(ask):
    print Fore.BLUE + u"@" + ask['asker'] + u" >> " + ask['message']

    response = emma.input(ask['message'], ask['asker'])
    if response != "%":
        print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "@" + ask['asker'] + " >> " + ask['message'] + "\n\n" + "emma >> " + response + "\n- - - - - - - - - - -\n" + emma.get_mood(update=False, expressAsText=True) + "\n\n"
        # todo: patch understanding back in, maybe move utilities.pretty_print_understanding() to this module?
        response = cgi.escape(response) # + "\n<!-- more -->\n" + cgi.escape(understanding)

        client_answer_ask(ask['id'], response.encode('utf-8'), ["dialogue", ask['asker'].encode('utf-8'), emma.get_mood().encode('utf-8')])
    else: print Fore.RED + "Generation failed."     # todo: attempt to reply multiple times (5?)

## Decision making
while True:
    askList = client_get_asks()
    print "Fetched %d asks." % len(askList)

    print "Choosing activity..."
    activities = ['reblog']
    activities.extend(['dream'] * 2)
    if len(askList) > 0: activities.extend(['answer'] * 3)

    activity = random.choice(activities)

    if activity = 'reblog':
        print "Reblogging a post..."
        reblog_post()
    elif activity = 'dream':
        print "Dreaming..."
        dream()
    elif activity = 'answer':
        print "Answering newest ask..."
            # todo: maybe have Emma figure out if she's able to respond to an ask before calling reply_to_asks()?
            reply_to_ask(askList[0])

    print "Sleeping for 15 minutes..."
    time.sleep(900)