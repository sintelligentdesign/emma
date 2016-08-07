# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          LEARNING, REPLY
import pytumblr
import cgi
import re

import apikeys
import settings

# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.tumblrConsumerKey,
    apikeys.tumblrConsumerSecret,
    apikeys.tumblrOauthToken,
    apikeys.tumblrOauthSecret
)

def get_asks():
    print "Checking Tumblr messages..."
    submissions = client.submission('emmacanlearn')     # todo: fix bug in which calling get_asks() more than once results in a 401 Unauthorized error
    askList = []
    if 'posts' in submissions.keys():       # temporary bugfix for above
        for submission in submissions['posts']: askList.append({'id': submission['id'], 'asker': submission['asking_name'], 'message': submission['question']})
    return askList

def delete_ask(askid):
    if settings.option('tumblr', 'enableAskDeletion'): 
        print "Deleting ask with ID %d..." % askid
        client.delete_post('emmacanlearn', askid)

def get_rebloggable_posts(user):
    posts = client.posts(user, type='text', filter='text')[u'posts']

    postList = []
    for post in posts:
        # Only allow posts that were posted by the blog owner and are also under 800 characters...
        if u'is_root_item' in post['trail'][0].keys() and len(post['body']) < 800:
            # ...But don't allow posts with tags in the realm of 'personal' or 'do not reblog'
            taggedDoNotReblog = False
            for tag in post['tags']:
                if re.sub(r'[\d\s\W]', "", tag.lower()) in [u"personal", u"donotreblog", u"dontreblog", u"dontrb", u"nsfw" u"epilepsywarning"]: taggedDoNotReblog = True
                elif re.sub(r'\d\W', " ", tag.lower()).startswith((u"trigger warning ", u"content warning ", u"tw ", u"cw")) or re.sub(r'\d\W', " ", tag.lower()).endswith((u" trigger warning", u" content warning", u" tw", u" cw")): taggedDoNotReblog = True
            if not taggedDoNotReblog: postList.append({'id': int(post['id']), 'reblogKey': post['reblog_key'], 'blogName': cgi.escape(post['blog_name']), 'body': post['body']})
    return postList

def post_text(body, tags=[]):
    if settings.option('tumblr', 'publishOutput'): client.create_text('emmacanlearn', state="published", body=body, tags=tags)

def post_ask(id, answer, tags=[]):
    if settings.option('tumblr', 'publishOutput'): client.edit_post('emmacanlearn', id=id, answer=answer, state='published', tags=tags, type='answer')

def reblog(postid, reblogKey, comment, tags):
    print "Reblogging post & adding comment..."
    if settings.option('tumblr', 'publishOutput'): client.reblog('emmacanlearn', id=postid, reblog_key=reblogKey, comment=cgi.escape(comment), tags=tags)