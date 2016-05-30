# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          INPUT, REPLY
# Writes/reads:
# Dependencies:     apikeys, pytumblr, pattern.web
# Dependency of:
import pytumblr
import pattern.web

import apikeys

# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.consumerKey,
    apikeys.consumerSecret,
    apikeys.oauthToken,
    apikeys.oauthSecret
)

# method for searching for new input when we find a new word
def search_for_text_posts(query):
    print "Searching Tumblr for posts about \"%s\"..." % query
    resultsList = client.tagged(query)          # note: tumblr returns 20 results by default. should we request more?
                                                # maybe we should request more if we fail to find any text posts on the first pass?
    textPosts = []
    for result in resultsList:
        resultType = result['type']             # separate out text posts from other post types
        if result['type'] == 'text':
            textPosts.append(result['body'])    # add each found post to a list
    print "Found %s text posts for \"%s\"" % (len(textPosts), query)
    for count, post in enumerate(textPosts):    # strip HTML from the text result
        textPosts[count] = pattern.web.plaintext(post)
    return textPosts

# get asks so that we can learn from them and generate responses
def get_messages():
    asks = client.submission('emmacanlearn.tumblr.com') # query tumblr API for messages
    asks = asks.values()                                # unwrap JSON
    asks = asks[0]
    #print asks
    messageList = []                                    # initialize return variable
    for ask in asks:                                    # suck out the stuff we care about
        askid = ask['id']
        asker = ask['asking_name']
        question = ask['question']
        message = (askid, asker, question)
        messageList.append(message)
    return messageList
    
# post our output to tumblr
def post_reply(asker, question, reply):
    asker = "@" + asker
    post = "%s >> %s\n\nemma >> %s" % (asker, question, reply)
    client.create_text("emmacanlearn", state="published", body=post, tags=["dialogue"])
    
def post_dream(thought):
    client.create_text("emmacanlearn", state="published", body=thought, tags=["dreams"])