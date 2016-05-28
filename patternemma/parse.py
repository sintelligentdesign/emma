import pattern.en

def tokenize(text):
    pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))

    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    for taggedSentence in taggedText:
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
        print "Parts of Speech: %s" % posSentence
        print "Sentence Chumks: %s" % chunkSeries
        print "Lemma: %s\n" % lemmaSentence
    return posSentence
    return chunkSeries
    return lemmaSentence

tokenize("I made a pretty whistle out of wood. It sounds good.")
tokenize("I am back.")
tokenize("He ate an apple. His friend watched longingly.")