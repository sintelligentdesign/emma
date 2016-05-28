import pattern.en

def tagText(text):
    pattern.en.pprint(pattern.en.parse(text, True, True, True, True, True))

    taggedText = pattern.en.parse(text, True, True, True, True, True).split()
    for taggedSentence in taggedText:
        # print taggedSentence
        posSentence = []
        chunkSeries = []
        lemmaSentence = []
        for taggedWord in taggedSentence:
            posSentence.append(taggedWord[1])
            chunkSeries.append(taggedWord[2])
            lemmaSentence.append(taggedWord[5])
        print posSentence
        print chunkSeries
        print lemmaSentence

# tagText("I made a pretty whistle out of wood. It sounds good.")
# tagText("I am back.")
tagText("He ate an apple. His friend watched longingly.")
