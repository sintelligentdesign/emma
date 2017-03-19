import math
import logging

from tqdm import tqdm
import pytumblr

import emma
import apikeys

logging.root.setLevel(1)

class Ask:
    def __init__(self, message, sender):
        self.message = message
        self.sender = sender

client = pytumblr.TumblrRestClient(
    apikeys.tumblrConsumerKey,
    apikeys.tumblrConsumerSecret,
    apikeys.tumblrOauthToken,
    apikeys.tumblrOauthSecret
)

# Connect to the blog and get number of posts
logging.info("Getting blog info...")
info = client.blog_info('emmacanlearn.tumblr.com')['blog']
numPosts = info['total_posts']

# Figure out how many requests we'll have to make
numRequests = int(math.ceil(numPosts/20))
logging.info("%d posts total." % numPosts)

asks = []
logging.info("Requesting posts & extracting messages...")
for i in tqdm(range(0, numRequests)):
    response = client.posts('emmacanlearn', filter='answer', offset=20*i)

    for post in response['posts']:
        if post['type'] == 'answer':
            asks.append(Ask(post['question'], post['asking_name']))

logging.info("Tokenizing messages and feeding them to Emma...")
for ask in asks:
    emma.train(ask.message, ask.sender)

logging.info("Done")