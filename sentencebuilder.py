# Name:             Sentence Generator
# Description:      Generates sentences based on what Emma knows about English and the world
# Section:          REPLY
import random
import re

import sqlite3 as sql
import pattern.en
from colorama import init, Fore
init(autoreset = True)

import utilities
from config import console, files

connection = sql.connect(files['dbPath'])
cursor = connection.cursor()

# Note: do not use greeting terms longer than 3 words
greetingTerms = [[u'what\'s', u'up'], [u'hi'], [u'hello'], [u'what', u'up'], [u'wassup'], [u'what', u'is', u'up'], [u'what\'s', u'going', u'on'], [u'how', u'are', u'you'], [u'howdy'], [u'hey']]

def generate_sentence(tokenizedMessage, asker=""):
    print "Creating reply..."
    print "Determining important words..."
    importantWords = []
    message = []
    for sentence in tokenizedMessage:
        for word in sentence:
            message.append(word[0])
            if word[1] in utilities.nounCodes and word[3] and word[0] not in importantWords:
                importantWords.append(word[0])
    
    # Make common sense halo
    print "Creating common sense halo..."
    halo = make_halo(make_halo(importantWords))

    print "important words: " + str(importantWords)
    print "halo: " + str(halo)

    # Find associations
    # Association package (information about bundle and the bundle itself) > Association bundle (word, all of its associations) > association (association type, target, weight)
    print "Creating association bundles..."
    primaryAssociations = bundle_associations(importantWords)
    secondaryAssociations = bundle_associations(halo)      # todo: create halo and get associations in one 
    
    #print primaryAssociations
    #print secondaryAssociations

    # Create packages which include the association package and information about its contents so that the generator knows what domains can be used
    print "Packaging associations and related information..."
    primaryPackage = make_association_package(primaryAssociations, asker)

    '''
    reply = ['%']
    remainingIntents = [random.choice(intents) for _ in range(len(intents))]
    while '%' in reply:
        if remainingIntents == []: return ['%']
        reply = random.choice(remainingIntents)
        remainingIntents.remove(reply)
        domainsExpanded = False
        while not domainsExpanded:
            print reply
            newReply = expand_domains(importantWords, reply)
            if reply == newReply: domainsExpanded = True
            reply = newReply
    
    reply[-1] += u"."
    reply[0] = reply[0][0].upper + reply[0][1:]

    for greeting in greetingTerms:
        match = re.match(' '.join(greeting), ' '.join(message[0:3]))
        if match:
            reply = [random.choice([u"Hi", u"Hello"]) + u",", u"@" + asker, u"!"] + reply
            break

    # Fix positions of punctuation, refer to Alex and Ellie as mom and dad
    for count, word in enumerate(reply):
        if word in [u"sharkthemepark", u"sharkthemeparks", u"@sharkthemepark"]: reply[count] = u"mom"
        elif word in [u"nosiron", u"nosirons", u"@nosiron"]: reply[count] = u"dad"
        elif word in [u",", u"!", u"?"]:
            reply[count - 1] += word
            del reply[count]

    return ' '.join(reply)
    '''

def make_halo(words):
    halo = []
    for word in words:
        with connection:
            cursor.execute("SELECT target FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.target = dictionary.word WHERE associationmodel.word = \'%s\' AND part_of_speech IN (\'NN\', \'NNS\', \'NNP\', \'NNPS\');" % word)
            for fetchedWord in cursor.fetchall():
                if fetchedWord not in words: halo.extend(fetchedWord)
    return halo

def bundle_associations(words):
    # Associations are bundled as tuples. The first object is the word, and the second object is an array containing the association type, target, and weight.
    associationPackage = []
    for word in words:
        print "Finding associations for \'%s\'..." % word
        with connection:
            cursor.execute("SELECT * FROM associationmodel WHERE word = \'%s\';" % word)
            SQLReturn = cursor.fetchall()
        if SQLReturn:
            associationBundle = []
            for row in SQLReturn:
                associationBundle.append([row[1], row[2], row[3]])
            associationPackage.append([word, associationBundle])
    return associationPackage

def choose_association(associations):
    dieSeed = 0
    for row in associations: dieSeed += row[3]
    dieResult = random.uniform(0, dieSeed)
    for row in associations:
        dieResult -= row[3]
        if dieResult <= 0:
            return row
            break

def make_association_package(associationBundle, asker):
    numObjects = 0
    hasAsker = False
    hasHas = False
    hasIsA = False
    
    numObjects = len(associationBundle)
    if asker != "": hasAsker = True

    associationPackage = []
    for associationGroup in associationBundle:
        for association in associationGroup[1]:
            if "HAS" in association[0]: hasHas = True
            if "IS-A" in association[0]: hasIsA = True
        associationPackage.append([hasHas, hasIsA, associationGroup])
    associationPackage = [{'numObjects': numObjects, 'hasAsker': hasAsker}, associationPackage]
    #print associationPackage
    return associationPackage

make_association_package([(u'blog', [[u'IS-A', u'blog', 0.0999999999997]]), (u'side', [[u'HAS-ABILITY-TO', u'know', 0.0999999999997], [u'HAS-ABILITY-TO', u'breathe', 0.0999999999997]]), (u'species', [[u'IS-OBJECT-OF', u'associate', 0.0999999999997], [u'IS-OBJECT-OF', u'be', 0.0999999999997], [u'IS-OBJECT-OF', u'live', 0.0999999999997], [u'HAS-ABILITY-TO', u'inhabit', 0.0999999999997]]), (u'matthew', [[u'HAS-ABILITY-TO', u'do', 0.0999999999997]]), (u'answer', [[u'HAS-ABILITY-TO', u'skip', 0.231969316683], [u'IS-OBJECT-OF', u'know', 0.0999999999997], [u'IS-OBJECT-OF', u'have', 0.231969316683], [u'IS-OBJECT-OF', u'come', 0.0999999999997], [u'IS-OBJECT-OF', u'inquire', 0.0999999999997], [u'IS-OBJECT-OF', u'find', 0.0999999999997], [u'IS-OBJECT-OF', u'validate', 0.0999999999997], [u'IS-OBJECT-OF', u'mean', 0.0999999999997], [u'IS-OBJECT-OF', u'die', 0.0999999999997], [u'IS-OBJECT-OF', u'name', 0.0999999999997]])], "sharkthemepark")

# Define intents
intents = ['COMPARATIVE', 'DECLARATIVE', 'IMPERATIVE', 'PHRASE']        # Greeting and Interrogative intents are special

greetingDomains = []
comparativeDomains = []
declarativeDomains = []
imperativeDomains = []
interrogativeDomains = []
phraseDomains = []

allowGreeting = False
allowComparative = False
allowDeclarative = False
allowImperative = False
allowInterrogative = False
allowPhrase = False

def makeGreeting():
    pass

def makeComparative():
    pass

def makeDeclarative():
    pass

def makeImperative():
    pass

def makeInterrogative():
    pass

def makePhrase():
    pass
    
generate_sentence([[[u'hi', u'UH', u'O', u'O'], [u'emma', u'NNP', u'B-NP', u'O'], [u'!', u'.', u'O', u'O']], [[u'sharkthemepark', 'NNP', u'B-NP', u'NP-SBJ-1'], [u'hope', u'VBP', u'B-VP', u'VP-1'], [u'emma', 'NNP', u'B-NP', u'NP-OBJ-1*NP-SBJ-2'], [u'be', u'VBP', u'B-VP', u'VP-2'], [u'do', u'VBG', u'I-VP', u'VP-2'], [u'well', u'RB', u'B-ADVP', u'O'], [u'.', u'.', u'O', u'O']], [[u'sharkthemepark', 'NNP', u'B-NP', u'NP-SBJ-1'], [u'like', u'VBP', u'B-VP', u'VP-1'], [u'dog', u'NNS', u'B-NP', u'NP-OBJ-1'], [u'because', u'IN', u'B-PP', u'O'], [u'dog', u'NNS', u'B-NP', u'NP-OBJ-1'], [u'be', u'VBP', u'B-VP', u'VP-2'], [u'gay', u'JJ', u'B-ADJP', u'O'], [u'.', u'.', u'O', u'O']]], u"sharkthemepark")