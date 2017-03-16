def determine_pronoun_references(message):
    pronouns = [
        "he", "him", "his", "himself",
        "she", "her", "hers", "herself",
        "they", "them", "their", "theirs", "themself", "themselves",
        "it", "its", "itself"
    ]

    # TODO: Rewrite all of this
    '''
    lastUsedNoun = list
    for sentence in message:
        for count, word in enumerate(sentence):
            if word[1] in ['NN', 'NNS', 'NNP', 'NNPS']:
                lastUsedNoun = word

            elif word[0] in pronouns and lastUsedNoun != list:
                print Fore.GREEN + u"Replacing pronoun \'%s\' with \'%s\'..." % (word[0], lastUsedNoun[0])
                sentence[count] = lastUsedNoun

    return message
    '''

def determine_posessive_references(sentence, asker):
    # todo: add "'s" for posessives (your -> emma's) when we're able to do something with posessives
    emmaReferences = [u"you", u"your", u"yours", u"yourself"]
    askerReferences = [u"i", u"my", u"mine", u"myself"]

    # TODO: Rewrite all of this
    '''
    for count, word in enumerate(sentence):
        if word[0] in posessiveReferences.keys():
            replacementWord = posessiveReferences[word[0]]
            print Fore.GREEN + u"replacing posessive reference \'%s\' with \'%s\'..." % (word[0], replacementWord)
            word[0] = replacementWord
            word[1] = u"NNP"
    return sentence
    '''