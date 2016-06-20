# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          LEARNING, REPLY
import pytumblr
import pattern.web

import apikeys
from config import tumblr

# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.tumblrConsumerKey,
    apikeys.tumblrConsumerSecret,
    apikeys.tumblrOauthToken,
    apikeys.tumblrOauthSecret
)

# method for searching for new input when we find a new word
def search_for_text_posts(query):
    print u"Searching Tumblr for posts about \"%s\"..." % query
    resultsList = client.tagged(query.encode('utf-8'))          # todo: tumblr returns 20 results by default. should we request more?
                                                # maybe we should request more if we fail to find any text posts on the first pass?
                                                # or maybe we could look them up using words API?
    textPosts = []
    # separate out text posts from other post types
    for result in resultsList:
        if result['type'] == 'text': textPosts.append(result['body'])

    print u"Found %d text posts for \"%s\"" % (len(textPosts), query)
    for count, post in enumerate(textPosts): textPosts[count] = pattern.web.plaintext(post)
    return textPosts

def get_messages():
    asksToGet = 10
    print "Getting Tumblr messages..."
    asks = client.submission('emmacanlearn.tumblr.com')
    asks = asks.values()        # unwrap JSON
    asks = asks[0]

    messageList = []
    for ask in asks:
        if asksToGet > 0:
            askid = ask['id']
            asker = ask['asking_name']
            question = ask['question']
            message = (askid, asker, question)
            messageList.append(message)

            asksToGet -= 1
    return messageList

def delete_ask(askid):
    client.delete_post(tumblr['username'], askid)

def post_reply(asker, question, reply):
    post = "@%s >> %s\n\nemma >> %s" % (asker, question, reply)
    post = post.encode('utf-8')
    client.create_text(tumblr['username'], state="published", body=post, tags=["dialogue", asker])

def post_dream(dream):
    dream = dream.encode('utf-8')
    client.create_text(tumblr['username'], state="published", body=dream, tags=["dreams"])