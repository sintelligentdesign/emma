# Name:             Settings / control panel
# Description:      Control panel for debugging, testing, further dev, fun, etc.
# Section:
from GUI import Window, CheckBox, application

general = {
    'chatMode': False,
    'enableSleep': False,
    'verboseLogging': False
}

tumblr = {
    'publishOutput': True,
    'enablePostPreview': True,

    'enableAskReplies': True,
    'enableAskDeletion': True,
    'fetchRealAsks': True,

    'enableReblogs': True,
    'enableDreams': True
}

paths = {
    'database': r'./emma.db',

    'moods': r'./moodHistory.p'
}