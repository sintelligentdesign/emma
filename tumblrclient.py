# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          LEARNING, REPLY
import pytumblr
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
        postList.append({'id': int(post['id']), 'reblogKey': post['reblog_key'], 'blogName': post['blog_name'], 'body': body})
    return postList

def post(body, tags=[]):
    if tumblr['enablePostPreview']: 
        tagsAsString = ""
        for tag in tags: tagsAsString += "#%s " % tag
        print Fore.BLUE + "\n\nTUMBLR POST PREVIEW\n\n" + Fore.RESET + "%s\n- - - - - - - - - - - - - - - - - - - - - - - - -\n%s\n\n" % (body, tagsAsString)
    if tumblr['enablePublishing']: client.create_text('emmacanlearn', state="published", body=body, tags=tags)
    else: print Fore.YELLOW + "!!! Posting disabled in config file."

def reblog(postid, reblogKey, blogName, comment, tags):
    if tumblr['enablePublishing']: client.reblog(blogName, id=postid, reblog_key=reblogKey, comment=comment, tags=tags)
    else: print Fore.YELLOW + "!!! Reblogging disabled in config file."