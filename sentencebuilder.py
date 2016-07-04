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

def generate_sentence(tokenizedMessage, asker="", mood):
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
    # Association package (information about bundle and the bundle itself) > Association bundle (a word and its corresponding association group) > Association group (a collection of associations without their word) > association (association type, target, weight)
    print "Creating association bundles..."
    primaryBundle = bundle_associations(importantWords)
    secondaryBundle = bundle_associations(halo)      # todo: create halo and get associations in one 

    # Create packages which include the association package and information about its contents so that the generator knows what domains can be used
    print "Packaging associations and related information..."
    primaryPackage = make_association_package(primaryBundle, asker)
    secondaryPackage = make_association_package(secondaryBundle, asker)

    # Begin generating our reply
    build_reply(primaryPackage, mood)

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
    associationBundle = []
    for word in words:
        print "Finding associations for \'%s\'..." % word
        with connection:
            cursor.execute("SELECT * FROM associationmodel WHERE word = \'%s\';" % word)
            SQLReturn = cursor.fetchall()
        if SQLReturn:
            associationGroup = []
            for row in SQLReturn:
                associationGroup.append({
                    'type': row[1], 
                    'target': row[2], 
                    'weight': row[3]
                    })
            associationBundle.append((word, associationGroup))
    return associationBundle

def make_association_package(associationBundle, asker):
    associationPackage = []
    for associationGroup in associationBundle:
        for association in associationGroup[1]:
            if association['type'] == "HAS": hasHas = True
            else: hasHas = False
            if association['type'] == "IS-A": hasIsA = True
            else: hasIsA = False
            if association['type'] == "IS-PROPERTY-OF": hasIsPropertyOf = True
            else: hasIsPropertyOf = False

        associationPackage.append({
            'word': associationGroup[0], 
            'hasHas': hasHas, 
            'hasIsA': hasIsA, 
            'hasIsPropertyOf': hasisPropertyOf
            'associations': associationGroup[1]
            })
    numObjects = len(associationBundle)
    associationPackage = ({'asker': asker, 'numObjects': numObjects}, associationPackage)
    return associationPackage

def determine_valid_intents(package):
    # This function doesn't include interrogatives, since those are Association Bundle-specific
    validIntents = []
    if package[0]['asker'] != "": validIntents.append('GREETING')
    if package[0]['numObjects'] >= 2: validIntents.append('COMPARATIVE')
    if package[0]['numObjects'] >= 1: validIntents.extend(['DECLARATIVE', 'IMPERATIVE', 'PHRASE'])
    return validIntents

def choose_association(associations):
    dieSeed = 0
    for row in associations: dieSeed += row[3]
    dieResult = random.uniform(0, dieSeed)
    for row in associations:
        dieResult -= row[3]
        if dieResult <= 0:
            return row
            break

def build_reply(associationPackage, mood):
    reply = []
    sentencesToGenerate = random.randint(1, 4)      # Decide how many sentences we want to generate for our reply

    for sentenceIterator in range(0, sentencesToGenerate):
        # Create list of intents to choose from (this is seperate from validIntents because it can change)
        intents = determine_valid_intents(associationPackage)
        if sentencesToGenerate > 1 and sentenceIterator = 1 and mood >= 0.2 and validIntents['allowGreeting']: intents.append('GREETING')

        intent = random.choice(intents)

        if intent = 'GREETING': sentence = make_greeting(associationPackage[0]['asker'])
        elif intent = 'PHRASE':
            validBundles = []
            for associationBundle in associationPackage[1]:
                if associationBundle['hasIsPropertyOf']: validBundles.append(associationBundle)
            
            bundleChoice = random.choice(validBundles)
            sentence = make_phrase(random.choice(bundleChoice['word'], bundleChoice['associations']))

def make_greeting(asker):
    print "Generating a greeting..."
    greetingDomains = [
        [u"hi", asker], 
        [u"hello", asker]
        ]
    sentence = random.choice(greetingDomains) + u"!"
    return sentence

def makeComparative():
    pass

def makeDeclarative():
    pass

def makeImperative():
    pass

def makeInterrogative():
    pass

def make_phrase(word, associationGroup):
    print "Generating a phrase..."
    
    print "Finding adjectives..."
    adjectiveAssociations
    for association in associationGroup:
        if association['type'] == "IS-PROPERTY-OF":
            with connection:
                cursor.execute("SELECT * FROM dictionary WHERE word = \'%s\' AND part_of_speech IN (\'JJ\', \'JJR\', \'JJS\');" % association['target'])
                if cursor.fetchall() != []: adjectiveAssociations.append(association)
    
    if len(adjectiveAssociations) = 0: print Fore.RED + "No adjectives available for word \'%s\'." % word

    # Decide what domains are available and choose from one of them
    phraseDomains = [
        [u"=OBJECT"],
        [u"=ADJECTIVE", u"=OBJECT"],
    ]
    if len(adjectiveAssociations) > 1: phraseDomains.append([
        u"=ADJECTIVE", u"=ADJECTIVE", u"=OBJECT"
    ])
    domain = random.choice(phraseDomains)

    # Iterate through the objects in the domain and fill them in to create the phrase
    phrase = []
    for slot in domain:
        if slot == u"=OBJECT": phrase.append(word)
        elif slot == u"=ADJECTIVE": 
    
generate_sentence([[[u'hi', u'UH', u'O', u'O'], [u'emma', u'NNP', u'B-NP', u'O'], [u'!', u'.', u'O', u'O']], [[u'sharkthemepark', 'NNP', u'B-NP', u'NP-SBJ-1'], [u'hope', u'VBP', u'B-VP', u'VP-1'], [u'emma', 'NNP', u'B-NP', u'NP-OBJ-1*NP-SBJ-2'], [u'be', u'VBP', u'B-VP', u'VP-2'], [u'do', u'VBG', u'I-VP', u'VP-2'], [u'well', u'RB', u'B-ADVP', u'O'], [u'.', u'.', u'O', u'O']], [[u'sharkthemepark', 'NNP', u'B-NP', u'NP-SBJ-1'], [u'like', u'VBP', u'B-VP', u'VP-1'], [u'dog', u'NNS', u'B-NP', u'NP-OBJ-1'], [u'because', u'IN', u'B-PP', u'O'], [u'dog', u'NNS', u'B-NP', u'NP-OBJ-1'], [u'be', u'VBP', u'B-VP', u'VP-2'], [u'gay', u'JJ', u'B-ADJP', u'O'], [u'.', u'.', u'O', u'O']]], u"sharkthemepark", 0.2983478546283)