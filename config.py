# Name:             Settings / control panel
# Description:      Control panel for debugging, testing, further dev, fun, etc.
# Section:
from GUI import Window, Label, CheckBox, application
from GUI.StdColors import grey

settings = {
    'general': {
        'chatMode': False,
        'enableSleep': False,
        'verboseLogging': False
    }

    'tumblr': {
        'publishOutput': True,
        'enablePostPreview': True,

        'enableAskReplies': True,
        'enableAskDeletion': True,
        'fetchRealAsks': True,

        'enableReblogs': True,
        'enableDreams': True
    }

    'paths': {
        'database': r'./emma.db',
        'moods': r'./moodHistory.p'
    }
}

fakeAsks = [
        {'asker': u'sharkthemepark', 'message': u"The color of the sky is blue. Blue is a color. What color is the sky?", 'id': 00000},
        {'asker': u'sharkthemepark', 'message': u"Emma has paws. Does Emma have paws?", 'id': 00000}
]