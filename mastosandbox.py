from mastodon import Mastodon
from mastodon import StreamListener

import re

# Create Mastodon API instance
mastodon = Mastodon(
    access_token = 'emma_usercred.secret',
    api_base_url = 'https://botsin.space'
)

class testListener(StreamListener):
    def on_update(self, status):
        # print status
        return True

    def on_notification(self, status):
        if status.type == 'mention':

            # Get status, remove HTML markup
            statusText = status.status.content
            statusText = re.sub('<[^<]+?>', '', statusText)
            print statusText

            # TODO: Filter out bots
            # TODO: Check if triggers for banned/blocked users
            # TODO: Incorporate "re: CW" in replies
            # TODO: Mirror visibility?

            return True
        else:
            return False

# Stream events
print mastodon.stream_user(
    listener=testListener()
)