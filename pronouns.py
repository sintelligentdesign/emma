# Gets a Message object and iterates through sentences/words, replacing pronouns with the last used noun
def determine_pronoun_references(message):
    # Ideally I'd split pronouns into personal pronouns (she/her) and object pronouns (it/its) 
    # so that the nouns that they reference could be tracked seperately
    # but there are people who use it/its and similar pronouns so idk :/
    pronouns = [
        'he', 'him', 'his', 'himself',
        'she', 'her', 'hers', 'herself',
        'they', 'them', 'their', 'theirs', 'themself', 'themselves',
        'it', 'its', 'itself'
    ]

    # TODO: Rewrite all of this
    '''
    lastUsedNoun = list
    for sentence in message:
        for count, word in enumerate(sentence):
            if word[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                lastUsedNoun = word

            elif word[0] in pronouns and lastUsedNoun != list:
                print Fore.GREEN + u'Replacing pronoun \'%s\' with \'%s\'...' % (word[0], lastUsedNoun[0])
                sentence[count] = lastUsedNoun

    return message
    '''

# Gets a Message object and the name of the person sending the message and replaces posessive references (you/me/your/my/etc.) with the thing that they reference
def determine_posessive_references(message, sender):
    # todo: add "'s" for posessives (your -> emma's) when we're able to do something with posessives
    emmaReferences = [u'you', u'your', u'yours', u'yourself']
    senderReferences = [u'i', u'my', u'mine', u'myself']

    for sentence in message.sentences:
        for word in sentence.words:
            if word.lemma in emmaReferences:
                print logging.info("Replacing posessive reference \'%s\' with \'%s\'..." % (word.lemma, 'emma'))
                word.lemma = u'emma'
                word.partOfSpeech = 'NNP'
            elif word.lemma in senderReferences:
                print logging.info("Replacing posessive reference \'%s\' with \'%s\'..." % (word.lemma, sender))
                word.lemma = sender
                word.partOfSpeech = 'NNP'
    
    return message