def determine_pronoun_references(message):
    """Gets a Message object and iterates through sentences/words, replacing pronouns with the last used noun"""
    # Ideally I'd split pronouns into personal pronouns (she/her) and object pronouns (it/its) 
    # so that the nouns that they reference could be tracked seperately
    # but there are people who use it/its and similar pronouns so idk :/
    pronouns = [
        u'he', u'him', u'his', u'himself',
        u'she', u'her', u'hers', u'herself',
        u'they', u'them', u'their', u'theirs', u'themself', u'themselves',
        u'it', u'its', u'itself'
    ]

    logging.DEBUG("Determining pronoun references...")
    lastUsedNoun = None
    for sentence in message.sentences:
        for word in sentence.words:
            # Check if the word is a noun and save it if it is
            if word.partOfSpeech in ['NN', 'NNS', 'NNP', 'NNPS']:
                lastUsedNoun = word
            
            # Check if the word is a pronoun and replace it if it is
            elif word.lemma in pronouns and lastUsedNoun != None:
                word.word = lastUsedNoun.word
                word.lemma = lastUsedNoun.lemma
                
    return message

def determine_posessive_references(message, sender):
    """Gets a Message object and the name of the person sending the message and replaces posessive references (you/me/your/my/etc.) with the thing that they reference"""
    # TODO: add "'s" for posessives (your -> emma's) when we're able to do something with posessives
    emmaReferences = [u'you', u'your', u'yours', u'yourself']
    senderReferences = [u'i', u'my', u'mine', u'myself']

    logging.DEBUG("Determining posessive references...")
    for sentence in message.sentences:
        for word in sentence.words:
            if word.lemma in emmaReferences:
                print logging.INFO("Replacing posessive reference \'%s\' with \'%s\'..." % (word.lemma, 'emma'))
                word.lemma = u'emma'
                word.partOfSpeech = 'NNP'
            elif word.lemma in senderReferences:
                print logging.INFO("Replacing posessive reference \'%s\' with \'%s\'..." % (word.lemma, sender))
                word.lemma = sender
                word.partOfSpeech = 'NNP'
    
    return message