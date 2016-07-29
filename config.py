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

def update_setting(setting):
    if setting in generalCheckboxMap.keys():
        group = 'general'
        value = generalCheckboxMap[setting]
    elif setting in tumblrCheckboxMap.keys():
        group = 'tumblr'
        value = tumblrCheckboxMap[setting]
    group[setting] = value

# General
generalLabel = make_label("General", color=grey, x=20, y=15)
enableChatModeBox = CheckBox(x=20, y=generalLabel.bottom, title="Chat mode", action=(update_setting, 'enableChatMode'))
enableSleepBox = CheckBox(x=20, y=enableChatModeBox.bottom, title="Enable sleep", action=(update_setting, 'enableSleep'))
verboseLoggingBox = CheckBox(x=20, y=enableSleepBox.bottom, title="Verbose Logging", action=(update_setting, 'verboseLogging'))

# Tumblr
tumblrLabel = make_label("Tumblr", color=grey, x=20, y=verboseLoggingBox.bottom+15)
publishOutputBox = CheckBox(x=20, y=tumblrLabel.bottom, title="Publish output", action=(update_setting, 'publishOutput'))
enablePostPreviewBox = CheckBox(x=20, y=publishOutputBox.bottom, title="Show post preview", action=(update_setting, 'enablePostPreview'))
enableAskRepliesBox = CheckBox(x=20, y=enablePostPreviewBox.bottom + 10, title="Enable Ask replies", action=(update_setting, 'enableAskReplies'))
enableAskDeletionBox = CheckBox(x=20, y=enableAskRepliesBox.bottom, title="Enable Ask deletion", action=(update_setting, 'enableAskDeletion'))
fetchRealAsksBox = CheckBox(x=20, y=enableAskDeletionBox.bottom, title="Fetch real Asks", action=(update_setting, 'fetchRealAsks'))
enableReblogsBox = CheckBox(x=20, y=fetchRealAsksBox.bottom + 10, title="Enable Reblogs", action=(update_setting, 'enableReblogs'))
enableDreamsBox = CheckBox(x=20, y=enableReblogsBox.bottom, title="Enable dreams", action=(update_setting, 'enableDreams'))

generalCheckboxMap = {'enableChatMode': enableChatModeBox.on, 'enableSleep': enableSleepBox.on, 'verboseLogging': verboseLoggingBox.on}
tumblrCheckboxMap = {'publishOutput': publishOutputBox.on, 'enablePostPreview': enablePostPreviewBox.on, 'enableAskReplies': enableAskRepliesBox.on, 'enableAskDeletion': enableAskDeletionBox.on, 'fetchRealAsks': fetchRealAsksBox.on, 'enableReblogs': enableReblogsBox.on, 'enableDreams': enableDreamsBox.on}

if general['enableChatMode']: enableChatModeBox.on = True
if general['enableSleep']: enableSleepBox.on = True
if general['verboseLogging']: verboseLoggingBox.on = True
if tumblr['publishOutput']: publishOutputBox.on = True
if tumblr['enablePostPreview']: enablePostPreviewBox.on = True
if tumblr['enableAskReplies']: enableAskRepliesBox.on = True
if tumblr['enableAskDeletion']: enableAskDeletionBox.on = True
if tumblr['fetchRealAsks']: fetchRealAsksBox.on = True
if tumblr['enableReblogs']: enableReblogsBox.on = True
if tumblr['enableDreams']: enableDreamsBox.on = True

win = Window(width=200, height=enableDreamsBox.bottom + 20, title="Emma Settings")

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