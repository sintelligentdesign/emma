# Name:             Settings / control panel
# Description:      Control panel for debugging, testing, further dev, fun, etc.
# Section:

debug = {
    # Enable or disable connecting to tumblr to fetch asks
    'fetchRealAsks': True,

    # If the above is false, supply a list of fake asks for Emma to read for testing and debugging
    'fakeAsks': [
        {'asker': u'sharkthemepark', 'message': u"The color of the sky is blue. Blue is a color. What color is the sky?", 'id': 00000},
        {'asker': u'sharkthemepark', 'message': u"Emma has paws. Does Emma have paws?", 'id': 00000},
        {'asker': u'sharkthemepark', 'message': u"Hey babe! It's me, your mom! I just wanted to drop in and say how proud I am of you. Keep it up!", 'id': 00000},
        {'asker': u'hotpizzapie', 'message': u"I think you're fantastic. I don't know what I'd do without you.", 'id': 00000},
        {'asker': u'nanopup', 'message': u"Hi Emma! I hope you're doing well. I like dogs because they are gay.", 'id': 00000},
        {'asker': u'sparkplugiv', 'message': u'hi emma im gay', 'id': 00000},
        {'asker': u'sharkthemepark', 'message': u"I love nanopup they're so perfect so pretty so pure i love that dog", 'id': 00000}],

    # Enable or disable sleeping between actions
    'enableSleep': True,

    # Enable or disable replying to asks
    'enableReplies': True,

    # Enable or disable reblogging posts
    'enableReblogs': True,

    # Enable or disable dreaming
    'enableDreams': True
}

console = {
    # Enable or disable verbose logging to the console while Emma is running
    'verboseLogging': False,

    # Enable or disable a mode where you can directly chat with Emma without going through Tumblr
    'chatMode': False
}

files = {
    # Specify what file Emma stores her information in
    'dbPath': r'./emma.db',

    # Specify what file Emma stores mood data in
    'moodPath': r'./moodHistory.p'
}

tumblr = {
    # Enable or disable posting on Tumblr (this also affects Reblogs)
    'enablePublishing': True,

    # Enable or disable Tumblr post previews, which give a rough idea of what a tumblr post will look like in the terminal
    'enablePostPreview': True,

    # Enable or disable deletion of asks after we're done with them
    'enableAskDeletion': True
}