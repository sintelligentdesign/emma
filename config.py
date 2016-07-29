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
# General
def update_general(setting):
    value = bool
    if setting in generalCheckboxMap.keys(): value = generalCheckboxMap[setting]
    general[setting] = value

enableChatModeBox = CheckBox(
    x = 20,
    y = 45,
    title = "Chat mode",
    action = (update_general, 'enableChatMode')
)
enableSleepBox = CheckBox(
    x = 20,
    y = enableChatModeBox.bottom,
    title = "Enable sleep",
    action = (update_general, 'enableSleep')
)
verboseLoggingBox = CheckBox(
    x = 20,
    y = enableSleepBox.bottom,
    title = "Verbose Logging",
    action = (update_general, 'verboseLogging')
)

generalCheckboxMap = {'enableChatMode': enableChatModeBox.on, 'enableSleep': enableSleepBox.on, 'verboseLogging': verboseLoggingBox.on}

win = Window(
    width = 500,
    height = 300,
    title = "Emma Settings Panel"
)
#    height = enableChatModeBox.bottom + 20,

def make_label(text, **kwds): return Label(text = text, **kwds)

win.add(make_label("General", color=grey, x = 20, y = 20))
win.add(enableChatModeBox)
win.add(enableSleepBox)
win.add(verboseLoggingBox)
win.show()

application().run()