# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          LEARNING, REPLY
import pytumblr
import pattern.web

import apikeys

# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.tumblrConsumerKey,
    apikeys.tumblrConsumerSecret,
    apikeys.tumblrOauthToken,
    apikeys.tumblrOauthSecret
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
            textPosts.append(result['body'])
    print "Found %s text posts for \"%s\"" % (len(textPosts), query)
    for count, post in enumerate(textPosts):
        textPosts[count] = pattern.web.plaintext(post)
    return textPosts

# get asks so that we can learn from them and generate responses
def get_messages():
    # query tumblr API for messages
    asks = client.submission('emmacanlearn.tumblr.com')
    asks = asks.values()        # unwrap JSON
    asks = asks[0]

    messageList = []
    for ask in asks:
        # suck out the stuff we care about
        askid = ask['id']
        asker = ask['asking_name']
        question = ask['question']
        message = (askid, asker, question)
        remove_message(askid)       # once we have the data we need, delete the ask
        messageList.append(message)
    return messageList
    
def remove_message(id):
    client.delete_post('emmacanlearn', id)

# post our output to tumblr
def post_reply(asker, question, reply):
    post = "@%s >> %s\n\nemma >> %s" % (asker, question, reply)
    client.create_text("emmacanlearn", state="published", body=post, tags=["dialogue", asker])

def post_dream(dream):
    client.create_text("emmacanlearn", state="published", body=dream, tags=["dreams"])
