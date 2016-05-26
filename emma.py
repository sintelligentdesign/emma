# -*- coding: utf-8 -*-

#   .ooooo.  ooo. .oo.  .oo.   ooo. .oo.  .oo.    .oooo.
#  d88' `88b `888P"Y88bP"Y88b  `888P"Y88bP"Y88b  `P  )88b
#  888ooo888  888   888   888   888   888   888   .oP"888
#  888    .,  888   888   888   888   888   888  d8(  888
#  `Y8bod8P' o888o o888o o888o o888o o888o o888o `Y888""8o
#
#  ·~-.¸¸,.-~*'¯¨'*·~-.¸,.-~*'¯¨'*·~-.¸¸,.-~*'¯¨'*·~-.¸¸,.
#
#          EXPANDING MODEL of MAPPED ASSOCIATIONS
#
#
#     Written by Ellie Cochran & Alexander Howard, with
#                contributions by Omri Barak.
#
#      Uses elements from the Natural Language Toolkit.
#                 Visit http://www.nltk.org.

import nltk                                             # Natural Language Toolkit
import conceptgen, posmodelgen                          # Learning packages
import sentencetemplategen, broca                       # Reply packages
import cfg, tumblrclient, utilities, sqlite3 as sql     # Misc.

# declare parts of speech umbrellas for generating replies
nounCodes = cfg.nounCodes()
verbCodes = cfg.verbCodes()
adjectiveCodes = cfg.adjectiveCodes()

def main():
    ### every loop, Emma decides what she wants to do.
    # todo: add choice cooldown
    # todo: add logic to decisions: try to keep new word list smallish, have a timer limit sleeping, default to "usually" answering questions
    decision = 0
    if decision == 0:       # Answer Tumblr questions
        conversate()
    elif decision == 1:     # Study new words
        learnwords()
    elif decision == 2:     # Sleep for 15 or so loops
        dream()

def conversate():
    ### Emma reads input, learns from it, and generates a response
    #   This will be replaced with Tumblr stuff later
    inputText = raw_input("You >> ")
    read(inputText, True)
        
def read(inputText, REPLY_BOOL):
    inputAsParagraph = inputText                                # todo: link this to tumblr, maybe have choice of input and output part of main()
    inputAsSentences = nltk.sent_tokenize(inputAsParagraph)     # segment the paragraph into a list of sentences
    inputAsWords = []                                           # segment each sentence into a list of words
    nounList = []
    
    for sentence in range(0, len(inputAsSentences)):
        ### for each sentence, run learning functions
        inputAsWords = nltk.word_tokenize(inputAsSentences[sentence])   # tokenize words in each sentence
        
        posmodelgen.grok(inputAsWords)                                  # learn sentence structure from the sentence's parts of speech pattern
        
        ## generate associations from the sentence
        inputPOSList = nltk.pos_tag(inputAsWords)                       # get the parts of speech for our sentence
        conceptgen.findassociations(inputAsWords, inputPOSList)         # look for associations and sent them to Emma's Concept Graph
        
        if REPLY_BOOL:
            ## find nouns in our input and add them to a noun list to help Emma choose what words to use when she responds
            inputAsPOS = []                                                 # define inputAsPOS
            for count in range(0, len(inputPOSList)):
                inputPOSTuple = inputPOSList[count]
                inputAsPOS.append(inputPOSTuple[1])

            for count in range(0, len(inputAsWords)):                       # create nounList
                if inputAsPOS[count] in nounCodes:
                    nounList.append(inputAsWords[count])
            nounList = utilities.consolidateduplicates(nounList)
            print "Noun List: %s" % str(nounList)
            reply(nounList)
    
def reply(nounList):
    ### now Emma generates a response
    # todo: have this loop n number of times to create multiple sentences
    generatesentence(nounList)

def learnwords():
    with open('emma.brn/newwords.txt') as newWordList:
        for line in newWordList:
            tumblrPosts = tumblrclient.searchfortextposts(line)
            for post in tumblrPosts:
                POSTaggedPost = nltk.pos_tag(post)
                conceptgen.findassociations(post, POSTaggedPost)
            
def dream():
    connection = sql.connect('emma.brn/conceptgraph.db')    # connect to the concept graph SQLite database
    cursor = connection.cursor()                            # get the cursor object
    for i in range(5):  # for now we'll tell Emma to have five dreams
        with connection:
            cursor.execute('SELECT noun FROM conceptgraph ORDER BY RANDOM() LIMIT 5;')   # choose 5 random nouns from Emma's concept graph
            nounList = cursor.fetchall()
        print "Dreaming about %s" % str(nounList)
        
        generatesentence(nounList)
    pass
    # loop
        # generate output
        # feed input to learning function with flags set to take direct input and not generate a response

def generatesentence(nounList):
    ## this function is seeded with a list of nouns (for the sentence to be "about"), and generates a sentence
    # generate a new sentence template from our template model
    replyTemplate = sentencetemplategen.generate()
    replyTemplate = nltk.word_tokenize(replyTemplate)
    
    # next, find verbs related to the seed nouns
    relatedVerbs = []
    for noun in nounList:
        relatedVerbs.append(broca.findrelatedverbs(noun))
    print "Related verbs: %s" % str(relatedVerbs)
    
    # try to insert our verbs into the sentence template
    broca.insertverbs(replyTemplate, relatedVerbs)
    print "Reply (verb pass complete): %s" % str(replyTemplate)
    
    # todo: do the rest of the sentence generation

while 1 > 0:
    main()