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

# get asks so that we can learn and generate responses
def getmessages():
    asks = client.submission('emmacanlearn.tumblr.com') # query tumblr API for messages
    asks = asks.values()                                # unwrap JSON
    asks = asks[0]
    asks = asks[0]
    asker = asks['asking_name']                         # suck out the stuff we care about
    question = asks['question']
    
    print "Asker: %s" % asker
    print "Question: %s" % question
    # todo: pack this into a tuple and return it
    # todo: see how this breaks for multiple asks