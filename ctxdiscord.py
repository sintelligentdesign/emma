import json

import requests
from colorama import init, Fore
init(autoreset=True)

import apikeys

# Add Emma to a server: https://discordapp.com/oauth2/authorize?client_id=220320669810950144&scope=bot&permissions=0

# It would be a lot easier to use discord.py instead of rolling my own solution
# But Emma is written in Python 2.7 and until I port the code to Python 3 this is how things have to be

clientHeaders = {
    'User-Agent': 'DiscordBot (http://www.emmacanlearn.tumblr.com, 0.0.4a)',
    'Authorization': 'Bot ' + apikeys.discordClientToken
    }

# Attempt to connect to Discord, test our connection
r = requests.get('https://discordapp.com/api/oauth2/applications/@me', headers=clientHeaders)

if not r.status_code == 200: print Fore.RED + "Connection error."
else:
    print Fore.GREEN + "Connected to Discord!"
    r = requests.get('https://discordapp.com/api/users/@me/guilds', headers=clientHeaders)
    print "Server List:"
    for guild in json.loads(r.text):
        print " * " guild['name']