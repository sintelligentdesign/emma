# Name:             Settings
# Description:      Includes functions related to checking the value of settings. Settings can be changed by hand or through a GUI using settingsfrontend module
# Section:
import json

settings = []
def load_settings():
    global settings
    with open('settings.json', 'r') as settingsFile: settings = json.load(settingsFile)
    return settings

def option(group, option): return settings[group][option]