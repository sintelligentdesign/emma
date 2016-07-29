# Name:             Settings / control win
# Description:      Control win for debugging, testing, further dev, fun, etc.
# Section:
from GUI import Window, Label, CheckBox, application
from GUI.StdColors import grey

general = {
    'enableChatMode': False,
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

fakeAsks = [
        {'asker': u'sharkthemepark', 'message': u"The color of the sky is blue. Blue is a color. What color is the sky?", 'id': 00000},
        {'asker': u'sharkthemepark', 'message': u"Emma has paws. Does Emma have paws?", 'id': 00000}
]

## GUI stuff begins here
def make_label(text, **kwds): return Label(text=text, **kwds)

# General
def update_general(setting):
    value = bool
    if setting in generalCheckboxMap.keys(): value = generalCheckboxMap[setting]
    general[setting] = value
generalLabel = make_label("General", color=grey, x=20, y=15)
enableChatModeBox = CheckBox(x=20, y=generalLabel.bottom, title="Chat mode", action=(update_general, 'enableChatMode'))
enableSleepBox = CheckBox(x=20, y=enableChatModeBox.bottom, title="Enable sleep", action=(update_general, 'enableSleep'))
verboseLoggingBox = CheckBox(x=20, y=enableSleepBox.bottom, title="Verbose Logging", action=(update_general, 'verboseLogging'))
generalCheckboxMap = {'enableChatMode': enableChatModeBox.on, 'enableSleep': enableSleepBox.on, 'verboseLogging': verboseLoggingBox.on}

# Tumblr
def update_tumblr(setting):
    value = bool
    if setting in tumblrCheckboxMap.keys(): value = tumblrCheckboxMap[setting]
    tumblr[setting] = value
tumblrLabel = make_label("Tumblr", color=grey, x=20, y=verboseLoggingBox.bottom+15)
publishOutputBox = CheckBox(x=20, y=tumblrLabel.bottom, title="Publish output", action=(update_tumblr, 'publishOutput'))
enablePostPreviewBox = CheckBox(x=20, y=publishOutputBox.bottom, title="Show post preview", action=(update_tumblr, 'enablePostPreview'))
enableAskRepliesBox = CheckBox(x=20, y=enablePostPreviewBox.bottom + 10, title="Enable Ask replies", action=(update_tumblr, 'enableAskReplies'))
enableAskDeletionBox = CheckBox(x=20, y=enableAskRepliesBox.bottom, title="Enable Ask deletion", action=(update_tumblr, 'enableAskDeletion'))
fetchRealAsksBox = CheckBox(x=20, y=enableAskDeletionBox.bottom, title="Fetch real Asks", action=(update_tumblr, 'fetchRealAsks'))
enableReblogsBox = CheckBox(x=20, y=fetchRealAsksBox.bottom + 10, title="Enable Reblogs", action=(update_tumblr, 'enableReblogs'))
enableDreamsBox = CheckBox(x=20, y=enableReblogsBox.bottom, title="Enable dreams", action=(update_tumblr, 'enableDreams'))
tumblrCheckboxMap = {'publishOutput': publishOutputBox.on, 'enablePostPreview': enablePostPreviewBox.on, 'enableAskReplies': enableAskRepliesBox.on, 'enableAskDeletion': enableAskDeletionBox.on, 'fetchRealAsks': fetchRealAsksBox.on, 'enableReblogs': enableReblogsBox.on, 'enableDreams': enableDreamsBox.on}

win = Window(width=200, height=enableDreamsBox.bottom + 20, title="Emma Settings Panel")

win.add(generalLabel)
win.add(enableChatModeBox)
win.add(enableSleepBox)
win.add(verboseLoggingBox)

win.add(tumblrLabel)
win.add(publishOutputBox)
win.add(enablePostPreviewBox)
win.add(enableAskRepliesBox)
win.add(enableAskDeletionBox)
win.add(fetchRealAsksBox)
win.add(enableReblogsBox)
win.add(enableDreamsBox)

win.show()
application().run()