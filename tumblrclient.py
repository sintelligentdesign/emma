# Name:             Tumblr client
# Description:      Communicates with Tumblr and executes related functions
# Section:          INPUT, REPLY
# Writes/reads:
# Dependencies:     apikeys, pytumblr
# Dependency of:
import apikeys, pytumblr

# authenticate with tumblr api
client = pytumblr.TumblrRestClient(
    apikeys.consumerKey,
    apikeys.consumerSecret,
    apikeys.oauthToken,
    apikeys.oauthSecret
)

# method for searching for new input when we find a new word
def searchfortextposts(query):
    print "Searching Tumblr for posts about \"%s\"..." % query
    resultsList = client.tagged(query)          # note: tumblr returns 20 results by default. should we request more?
                                                # maybe we should request more if we fail to find any text posts on the first pass?
    textPosts = []
    for result in resultsList:
        resultType = result['type']             # separate out text posts from other post types
        if result['type'] == 'text':
            textPosts.append(result['body'])    # add each found post to a list
    print "Found %s text posts for %s" % (len(textPosts), query)
    for post in textPosts:                      # strip HTML from the text result
        # todo: strip html
        pass
    return textPosts

# get asks so that we can learn from them and generate responses
def getmessages():
    asks = client.submission('emmacanlearn.tumblr.com') # query tumblr API for messages
    asks = asks.values()                                # unwrap JSON
    asks = asks[0]
    
    messageList = []                                    # initialize return variable
    for ask in asks:                                    # suck out the stuff we care about
        asker = ask['asking_name']
        question = ask['question']
        message = (asker, question)                     # package the message as a tuple
        messageList.append(message)                     # add message tuple to message list
    return messageList
    
# post our output to tumblr
def post(ask, reply):
    postBody = ask + "\n\n" + reply
    client.create_text("emmacanlearn", state="published", body=postBody)