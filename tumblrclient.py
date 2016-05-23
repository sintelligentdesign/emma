import apikeys, pytumblr, json

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
    asks = client.submission('emmacanlearn.tumblr.com')
    print asks