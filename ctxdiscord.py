import requests

import apikeys

# It would be a lot easier to use discord.py instead of rolling my own solution
# But Emma is written in Python 2.7 and until I port the code to Python 3 this is how things have to be

clientHeaders = {
    'User-Agent': 'DiscordBot (http://www.emmacanlearn.tumblr.com, 0.0.4a)',
    'Authorization': 'Bot ' + apikeys.discordClientToken
    }

# Test our connection
r = requests.get('https://discordapp.com/api/oauth2/applications/@me', headers=clientHeaders)
if r.status_code == "200":
    print "Connected to Discord!"
    # todo: pprint name, id
elif r.status_code == "401":
    print "Permissions error."
    # todo: add flavor text
else:
    print "Discord connection failed."
    # todo: retry in 30s