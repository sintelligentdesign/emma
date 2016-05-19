#delete me later
import nltk, re, pprint

sentencepos = []

def preprocess(sentence):
    # get the parts of speech from the input
    sentence = nltk.sent_tokenize(sentence)                         # NLTK default sentence segmenter (todo: this should go in the main logic later)
    #sentence = [nltk.word_tokenize(sent) for sent in sentences]    # NLTK default word tokenizer (todo: this should go in the main logic later)
                                                                    # note: do we want to use the multi word expression tokenizer instead (to help with glue words)?
    sentence = nltk.word_tokenize(str(sentence).strip('[]'))      
    sentence = nltk.pos_tag(sentence)                               # NLTK default part-of-speech tagger
    print sentence
    
    # extract parts of speech as array from tuple
    for count in range (0, len(sentence)):
        sentencepos.append(sentence[count])
        print sentencepos
    
input = raw_input('INPUT >> ')
preprocess(input)