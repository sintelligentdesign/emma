# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          LEARNING, REPLY
import pytumblr
import cgi
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

def get_asks():
    print "Checking Tumblr messages..."
    asks = client.submission('emmacanlearn.tumblr.com')

    askList = []
    for ask in asks.values()[0]: askList.append({'id': int(ask['id']), 'asker': ask['asking_name'], 'message': ask['question']})
    return askList

def delete_ask(askid):
    if tumblr['enableAskDeletion']: 
        print "Deleting ask with ID %d..." % askid
        client.delete_post('emmacanlearn', askid)
    else: print Fore.YELLOW + "!!! Ask deletion disabled in config file."

def get_recent_posts(user):
    print "Fetching @%s\'s most recent text posts..." % user
    posts = client.posts(user, type='text', filter='text')[u'posts']

    postList = []
    for post in posts:
        # Only allow posts that were posted by the blog owner and are also under 800 characters...
        if u'is_root_item' in post['trail'][0].keys() and len(post['body']) < 800:
            # ...But don't allow posts with tags in the realm of 'personal' or 'do not reblog'
            taggedDoNotReblog = False
            for tag in post['tags']:
                if re.sub(r'[\d\s\W]', "", tag.lower()) in [u"personal", u"donotreblog", u"dontreblog"]: taggedDoNotReblog = True
            if not taggedDoNotReblog: postList.append({'id': int(post['id']), 'reblogKey': post['reblog_key'], 'blogName': cgi.escape(post['blog_name']), 'body': post['body']})
    return postList

def post(body, tags=[]):
    if tumblr['enablePostPreview']: 
        tagsAsString = ""
        for tag in tags: tagsAsString += "#%s " % tag
        print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "%s\n- - - - - - - - - - - - - - - - - - - - - - - - -\n%s\n\n" % (body, tagsAsString)
    if tumblr['enablePublishing']: client.create_text('emmacanlearn', state="published", body=body, tags=tags)
    else: print Fore.YELLOW + "!!! Posting disabled in config file."

def reblog(postid, reblogKey, comment, tags):
    print "Reblogging post & adding comment..."
    if tumblr['enablePublishing']: client.reblog('emmacanlearn', id=postid, reblog_key=reblogKey, comment=cgi.escape(comment), tags=tags)
    else: print Fore.YELLOW + "!!! Reblogging disabled in config file."