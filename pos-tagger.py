#delete me later
import nltk, re, pprint

def preprocess(document):
    sentences = nltk.sent_tokenize(document)                        # NLTK default sentence segmenter
    print sentences
    sentences = [nltk.word_tokenize(sent) for sent in sentences]    # NLTK default word tokenizer
    print sentences
    sentences = [nltk.pos_tag(sent) for sent in sentences]          # NLTK default part-of-speech 
    print sentences
    return sentences
    
input = raw_input('INPUT >> ')
preprocess(input)