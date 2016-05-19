#delete me later
import nltk, re, pprint

def preprocess(document):
    sentences = nltk.sent_tokenize(document)                        # NLTK default sentence segmenter
    print sentences
    sentences = nltk.word_tokenize(str(sentences).strip('[]\''))          # NLTK default word tokenizer
    print sentences
    sentences = nltk.pos_tag(sentences)          # NLTK default part-of-speech
    print sentences
    tagsentence = ""
    for count in range(0, len(sentences)):         # makes sentence of tags from list of tuples
        tup = sentences[count]
        tagsentence += tup[1] + " "
    print tagsentence
    return tagsentence

input = raw_input('INPUT >> ')
preprocess(input)
