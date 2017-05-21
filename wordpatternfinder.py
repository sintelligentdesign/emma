class InterrogativePackage:
    def __init__(self):
        pass

def find_patterns(message):
    for sentence in message.sentences:
        # If the sentence ends in a question mark, it's proabably interrogative
        if sentence.words[-1].word == u"?":
            sentence.domain = 'interrogative'
        