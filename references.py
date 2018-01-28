import logging

def determine_references(message, ask):
    """Gets a Message object and iterates through sentences/words, replacing pronouns with the last used noun and posessive references with the thing that they reference. Returns a new unicode string"""
    # Ideally I'd split pronouns into personal pronouns (she/her) and object pronouns (it/its) 
    # so that the nouns that they reference could be tracked seperately
    # but there are people who use it/its and similar pronouns so idk :/
    pronouns = [
        u'he', u'him', u'his', u'himself',
        u'she', u'her', u'hers', u'herself',
        u'they', u'them', u'their', u'theirs', u'themself', u'themselves',
        u'it', u'its', u'itself'
    ]

    # TODO: add "'s" for posessives (your -> emma's) when we're able to do something with posessives
    emmaReferences = [u'you', u'your', u'yours', u'yourself']
    senderReferences = [u'i', u'my', u'mine', u'myself']

    logging.debug("Determining pronoun references...")
    lastUsedNoun = None

    newSentence = u''
    for sentence in message.sentences:
        for word in sentence.words:
            logging.debug("lastUsedNoun: {0}".format(lastUsedNoun))

            # Check if the word is a noun and save it if it is
            if word.type in ['NN', 'NNS', 'NNP', 'NNPS']:
                lastUsedNoun = word.string
                newSentence += word.string + u' '
            
            # Check if the word is a pronoun and replace it if it is
            elif word.lemma in pronouns and lastUsedNoun != None:
                newSentence += lastUsedNoun + u' '

            # Check if the word references emma
            elif word.lemma in emmaReferences:
                lastUsedNoun = u'emma'
                newSentence += u'emma '

            # Check if the word references the sender
            elif word.lemma in senderReferences:
                newSentence += ask.sender + u' '

            # Otherwise just dump the word into the new sentence
            else:
                newSentence += word.string + u' '
                
    logging.debug("Pronoun references pass: {0}".format(newSentence))
    return newSentence