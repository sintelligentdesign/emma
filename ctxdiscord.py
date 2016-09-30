import json
import time

import requests
from colorama import init, Fore
init(autoreset=True)

#import emma
import apikeys

# Add Emma to a server: https://discordapp.com/oauth2/authorize?client_id=220320669810950144&scope=bot&permissions=0

# It would be a lot easier to use discord.py instead of rolling my own solution
# But Emma is written in Python 2.7 and until I port the code to Python 3 this is how things have to be

def make_headers(extraHeaders={}):
    defaultHeaders = {
        "User-Agent": "DiscordBot (http://www.emmacanlearn.tumblr.com, 0.0.4a)",
        "Authorization": "Bot " + apikeys.discordClientToken
    }
    return dict(defaultHeaders.items() + extraHeaders.items())

# Attempt to connect to Discord, test our connection
r = requests.get('https://discordapp.com/api/oauth2/applications/@me', headers=make_headers())
print r.text

if not r.status_code == 200: print Fore.RED + "Connection error."
else:
    print Fore.GREEN + "Connected to Discord!"

    # Get and display server list
    r = requests.get('https://discordapp.com/api/users/@me/guilds', headers=make_headers())
    print "Guild/Channel List:"
    connectedChannels = []
    for guild in json.loads(r.text): 
        print " * " + guild['name'] + " [" + guild['id'] + "]"
        
        for channel in json.loads(requests.get('https://discordapp.com/api/guilds/' + guild['id'] + "/channels", headers=make_headers()).text):
            if channel['type'] == 'text': 
                print "   - " + channel['name'] + " [" + channel['id'] + "]"
                # todo: add channel parent guild (and guild id?) to connectedChannels objects
                connectedChannels.append({'name': channel['name'], 'id': channel['id']})
    print connectedChannels

                
    # Mention listen loop
    while True:
        # todo: check rate limits
        for channel in connectedChannels:
            messages = json.loads(requests.get('https://discordapp.com/api/channels/' + channel['id'] + '/messages', headers=make_headers()).text)

            for message in messages:
                if message['content'].startswith(u"<@220320669810950144>"):
                    ## If Emma is @ mentioned, take note and generate a response
                    print Fore.BLUE + "Mentioned on " + channel['name'] + "!"
                    print message['author']['username'] + ": " + message['content']

                    # Read message and generate response
                    #response = emma.input(message['content'].lstrip(u"<@220320669810950144>"), message['author']['username'])
                    response = "test"

                    # Post response
                    r = requests.post(
                        'https://discordapp.com/api/channels/' + channel['id'] + '/messages', 
                        headers=make_headers({"Content-Type": "application/json"}), 
                        json={"content": response.encode('utf-8')}
                    )
                    print r.text
    time.sleep(30)