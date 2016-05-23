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
    resultsList = client.tagged(query)      # note: tumblr returns 20 results by default. should we request more?
    for count in range(0, len(resultsList)):
        result = resultsList[count]
        resultType = result['type']
        if result['type'] == 'text':
            print "Body of result %s" % count
            print result['body']
            # todo: strip html and get just strings
            # todo: fail elegantly if we find no text results

# get asks so that we can learn and generate responses
def getmessages():
    asks = client.submission('emmacanlearn.tumblr.com') # query tumblr API for messages
    asks = asks.values()                                # unwrap JSON
    asks = asks[0]
    
    messageList = {}                                    # initialize return variable
    for count in range(0, len(asks)):                   # suck out the stuff we care about
        currentAsk = asks[count]
        asker = currentAsk['asking_name']
        question = currentAsk['question']
        messageList[question] = asker                   # add message to message list dictionary
                                                        # messages are stored with the user as the value so that multiple messages from one user don't overwrite that user's old messages
    return messageList