# Name:             Settings
# Description:      Control panel for debugging, testing, further dev, fun, etc.
# Section:
import json

settings = []
def load_settings():
    global settings
    with open('settings.json', 'r') as settingsFile: settings = json.load(settingsFile)
    return settings

def option(group, option): return settings[group][option]