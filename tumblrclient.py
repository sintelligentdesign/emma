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
    print resultsList

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