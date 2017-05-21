import misc

class InterrogativePackage:
    """
    Packages the important bits of question nicely

    Class variables:
    questionType    str     Type of question ('what is', 'do X have Y', etc.)
    attribute       Word    Half of the important question bits ('what is the color of the sky?' <- 'color')
    subject         Word    The other half ('what is the color of the sky?' <- 'sky')
    """

    def __init__(self, questionType, attribute, subject):
        self.questionType = questionType
        self.attribute = attribute
        self.subject = subject

def package_interrogatives(sentence):
    # "What is...?"
    if sentence.words[0].lemma == u'what':
        if sentence.words[1].lemma == u'be':
            for word in sentence.words[2:]:
                if word.partOfSpeech in misc.nounCodes:
                    attribute = word
                    break
            for word in sentence.words[attribute.index + 1:]:
                if word.partOfSpeech in misc.nounCodes:
                    subject = word
                    break
            package = InterrogativePackage('WHAT-IS', attribute, subject)
            return package

def find_patterns(message):
    for sentence in message.sentences:
        # If the sentence ends in a question mark, it's proabably interrogative
        if sentence.words[-1].word == u'?':
            sentence.domain = 'INTERROGATIVE'
        # If the sentence starts with a wh-part of speech, it's also probably interrogative
        if sentence.words[0].partOfSpeech in misc.whWordCodes:
            sentence.domain = 'INTERROGATIVE'

        # If the sentence begins with "(noun) is...", we're probably being told this and shouldn't ask about it
        if sentence.words[0].partOfSpeech in misc.nounCodes:
            if sentence.words[1].lemma == u'be':
                sentence.domain = 'DECLARATIVE'

        if sentence.domain == 'INTERROGATIVE':
            # TODO: Do package_interrogatives()
            pass

    return message