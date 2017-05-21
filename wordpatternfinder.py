import misc

class InterrogativePackage:
    def __init__(self):
        pass

def find_patterns(message):
    for sentence in message.sentences:
        # If the sentence ends in a question mark, it's proabably interrogative
        if sentence.words[-1].word == u"?":
            sentence.domain = 'interrogative'
        # If the sentence starts with a wh-part of speech, it's also probably interrogative
        if sentence.words[0].partOfSpeech in misc.whWordCodes:
            sentence.domain = 'interrogative'

        # If the sentence begins with "(noun) is...", we're probably being told this and shouldn't ask about it
        if sentence.words[0].partOfSpeech in misc.nounCodes:
            if sentence.words[1].lemma == u'be':
                sentence.domain = 'declarative'