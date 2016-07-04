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

def generate_sentence(tokenizedMessage, mood, asker=""):
    # todo: optimize sentence generation
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

    # Find associations
    # Association package (information about bundle and the bundle itself) > Association bundle (a word and its corresponding association group) > Association group (a collection of associations without their word) > association (association type, target, weight)
    print "Creating association bundles..."
    primaryBundle = bundle_associations(importantWords)
    secondaryBundle = bundle_associations(halo)

    # Create packages which include the association package and information about its contents so that the generator knows what domains can be used
    print "Packaging associations and related information..."
    primaryPackage = make_association_package(primaryBundle, asker)
    secondaryPackage = make_association_package(secondaryBundle, asker)

    # Begin generating our reply
    reply = build_reply(primaryPackage, mood)
    return finalize_reply(reply)

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
            if association['type'] == "HAS-PROPERTY": hasHasProperty = True
            else: hasHasProperty = False
            if association['type'] == "HAS-ABILITY-TO": hasHasAbilityTo = True
            else: hasHasAbilityTo = False

        associationPackage.append({
            'word': associationGroup[0], 
            'hasHas': hasHas, 
            'hasIsA': hasIsA, 
            'hasHasProperty': hasHasProperty,
            'hasHasAbilityTo': hasHasAbilityTo,
            'associations': associationGroup[1]
            })
    numObjects = len(associationBundle)
    associationPackage = ({'asker': asker, 'numObjects': numObjects}, associationPackage)
    return associationPackage

def determine_valid_intents(associationPackage):
    # This function doesn't include interrogatives or greetings, since those are Association Bundle-specific
    validIntents = {}
    for associationBundle in associationPackage[1]:
        intents = []
        if associationBundle['hasHasProperty']: intents.append('DECLARATIVE')
        if associationPackage[0]['numObjects'] >= 2 and 'DECLARATIVE' in intents: intents.append('COMPARATIVE')
        if associationBundle['hasHasAbilityTo']: intents.append('IMPERATIVE')
        if associationPackage[0]['numObjects'] >= 1: intents.append('PHRASE')
        validIntents[associationBundle['word']] = intents
    return validIntents

def choose_association(associationGroup):
    dieSeed = 0
    for association in associationGroup:
        dieSeed += association['weight']
    dieResult = random.uniform(0, dieSeed)

    for association in associationGroup:
        dieResult -= association['weight']
        if dieResult <= 0:
            return association
            break

def build_reply(associationPackage, mood):
    reply = []
    sentencesToGenerate = random.randint(1, 4)      # Decide how many sentences we want to generate for our reply

    for sentenceIterator in range(0, sentencesToGenerate):
        print "Generating sentence %d of %d..." % (sentenceIterator + 1, sentencesToGenerate)

        # Create list of words and intents to choose from
        validIntents = determine_valid_intents(associationPackage)
        print "Valid intents: " + str(validIntents)

        # If conditions are right, add "GREETING" intent to the list of intents
        if sentencesToGenerate > 1 and sentenceIterator == 1 and mood >= 0.2 and associationPackage[0]['asker'] != "": 
            for word, intents in validIntents.iteritems(): validIntents[word] = intents + ['GREETING']

        word = random.choice(validIntents.keys())
        intent = random.choice(validIntents[word])

        for associationBundle in associationPackage[1]:
            if associationBundle['word'] == word: associationBundle = associationBundle

        # Decide whether to make objects in the sentence plural
        if random.randint(0, 1) == 0: pluralizeObjects = True
        else: pluralizeObjects = False

        print "Intent: " + intent

        # Fill in our chosen intent
        if intent == 'GREETING': sentence = make_greeting(associationPackage[0]['asker']) + [u"!"]

        elif intent == 'PHRASE': sentence = make_phrase(associationBundle['word'], associationBundle['associations'], pluralizeObjects) + [u"."]

        elif intent == 'DECLARATIVE':
            bundleInfo = {'hasHas': associationBundle['hasHas'], 'hasIsA': associationBundle['hasIsA'], 'hasHasProperty': associationBundle['hasHasProperty']}
            sentence = make_declarative(associationBundle['word'], associationBundle['associations'], pluralizeObjects, bundleInfo) + [u"."]

        elif intent == 'COMPARATIVE':
            wordsToCompare = []
            for word in validIntents.keys():
                if 'COMPARATIVE' in validIntents[word]:
                    wordsToCompare.append(word)
            comparisonChoices = []
            for word in wordsToCompare:
                for associationBundle in associationPackage[1]:
                    if associationBundle['word'] == word: comparisonChoices.append(associationBundle)
            sentence = make_comparative(associationBundle, random.choice(comparisonChoices), pluralizeObjects)

        elif intent == 'IMPERATIVE':
            bundleInfo = {'hasHas': associationBundle['hasHas'], 'hasIsA': associationBundle['hasIsA'], 'hasHasProperty': associationBundle['hasHasProperty'], 'hasHasAbilityTo': associationBundle['hasHasAbilityTo']}
            sentence = make_imperative(associationBundle['word'], associationBundle['associations'], pluralizeObjects) + [u"."]

        else: sentence = [intent]
        sentence[0] = sentence[0][0].upper() + sentence[0][1:]
        print sentence
        reply.extend(sentence)
    
    return reply

def make_greeting(asker):
    print "Generating a greeting..."
    greetingDomains = [
        [u"hi", asker], 
        [u"hello", asker]
        ]
    return random.choice(greetingDomains)

def make_comparative(associationBundle, comparisonBundle, pluralizeObjects):
    print "Generating a comparative statement for \'%s\' and \'%s\'..." % (associationBundle['word'], comparisonBundle['word'])

    print "Choosing domain..."
    comparativeDomains = [
        [u"=DECLARATIVE", u"like", u"=COMPARISON"],
        [u"=DECLARATIVE", u",", u"and", u"=COMPARISON"],
        [u"=DECLARATIVE", u",", u"but", u"=COMPARISON"]
    ]
    domain = random.choice(comparativeDomains)

    print "Building comparative statement..."
    sentence = []
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=DECLARATIVE":
            bundleInfo = {'hasHas': associationBundle['hasHas'], 'hasIsA': associationBundle['hasIsA'], 'hasHasProperty': associationBundle['hasHasProperty']}
            sentence.extend(make_declarative(associationBundle['word'], associationBundle['associations'], pluralizeObjects, bundleInfo))
        elif slot == u"=COMPARISON":
            bundleInfo = {'hasHas': comparisonBundle['hasHas'], 'hasIsA': comparisonBundle['hasIsA'], 'hasHasProperty': comparisonBundle['hasHasProperty']}
            sentence.extend(make_declarative(comparisonBundle['word'], comparisonBundle['associations'], pluralizeObjects, bundleInfo))
        else: sentence.append(slot)

    return sentence

def make_declarative(word, associationGroup, pluralizeObjects, bundleInfo):
    print "Generating a declarative statement for \'%s\'..." % word
    
    hasAssociations = []
    isaAssociations = []
    ispropertyofAssociations = []
    if bundleInfo['hasHas']:
        for association in associationGroup:
            if association['type'] == "HAS": hasAssociations.append(association)
    if bundleInfo['hasIsA']:
        for association in associationGroup:
            if association['type'] == "IS-A": isaAssociations.append(association)
    for association in associationGroup:
        if association['type'] == "HAS-PROPERTY": ispropertyofAssociations.append(association)

    print "Choosing domain..."
    declarativeDomains = [
        [u"=OBJECT", u"=ISARE", u"=ADJECTIVE"]
    ]
    if len(ispropertyofAssociations) > 1: declarativeDomains.append(
        [u"=OBJECT", u"=ISARE", u"=ADJECTIVE", u"and", u"=ADJECTIVE"]
    )
    if bundleInfo['hasHasAbilityTo']: declarativeDomains.append(
        [u"=OBJECT", u"=ACTION"],
        [u"=OBJECT", u"can", u"=ACTION"]
    )
    if hasAssociations != []: declarativeDomains.append(
        [u"=OBJECT", u"=HAVEHAS", u"=OBJHAS"]
    )
    if isaAssociations != []: declarativeDomains.append(
        [u"=OBJECT", u"=ISARE", u"=OBJISA"]
    )
    domain = random.choice(declarativeDomains)

    print "Building declarative statement..."
    sentence = []
    # Iterate through the objects in the domain and fill them in to create the declarative statement
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=OBJECT": sentence.extend(make_phrase(word, associationGroup, pluralizeObjects))
        elif slot == u"=ADJECTIVE": sentence.append(choose_association(ispropertyofAssociations)['target'])
        elif slot == u"=ACTION": sentence.append(make_imperative(word, associationGroup, pluralizeObjects))
        elif slot == u"=OBJHAS": sentence.append(choose_association(hasAssociations)['target'])
        elif slot == u"=OBJISA": sentence.append(choose_association(isaAssociations)['target'])
        elif slot == u"=ISARE":
            if pluralizeObjects: sentence.append(u"are")
            else: sentence.append(u"is")
        elif slot == u"=HAVEHAS":
            if pluralizeObjects: sentence.append(u"have")
            else: sentence.append(u"has")
        else: sentence.append(slot)

    return sentence

def make_imperative(word, associationGroup, pluralizeObjects):
    print "Generating an imperative statement for \'%s\'..." % word

    print "Looking for verb associations..."
    verbAssociations = []
    for association in associationGroup:
        if association['type'] == "HAS-ABILITY-TO": verbAssociations.append(association)

    if len(verbAssociations) == 0: print Fore.YELLOW + "No verbs available for \'%s\'!" % word

    print "Choosing domain..."
    imperativeDomains = [
        [u"=VERB", u"=OBJECT"],
        [u"=VERB", u"the", u"=OBJECT"],
        [u"always", u"=VERB", u"=OBJECT"],
        [u"never", u"=VERB", u"=OBJECT"]
    ]
    if not pluralizeObjects: imperativeDomains.append(
        [u"=VERB", u"a", u"=OBJECT"]
    )
    # todo: VERB a/an/the OBJECT with its (THING OBJECT HAS / a/an/the OTHER OBJECT)
    domain = random.choice(imperativeDomains)
    
    print "Building sentence..."
    sentence = []
    for count, slot in enumerate(sentence):
        print sentence + domain[count:]
        if slot == "=OBJECT": sentence.extend(make_phrase(word, associationGroup, pluralizeObjects))
        elif slot == "=VERB": sentence.append(choose_association(verbAssociations)['target'])
        else: sentence.append(slot)

    return sentence

def make_interrogative():
    pass

def make_phrase(word, associationGroup, pluralizeObjects):
    print "Generating a phrase for \'%s\'..." % word
    
    print "Looking for adjective associations..."
    adjectiveAssociations = []
    for association in associationGroup:
        if association['type'] == "HAS-PROPERTY":
            with connection:
                cursor.execute("SELECT * FROM dictionary WHERE word = \'%s\' AND part_of_speech IN (\'JJ\', \'JJR\', \'JJS\');" % association['target'])
                if cursor.fetchall() != []: adjectiveAssociations.append(association)
    
    if len(adjectiveAssociations) == 0: print Fore.YELLOW + "No adjectives available for \'%s\'!" % word

    print "Choosing domain..."
    phraseDomains = [
        [u"=OBJECT"]
    ]
    if len(adjectiveAssociations) >= 1: phraseDomains.append(
        [u"=ADJECTIVE", u"=OBJECT"]
    )
    if len(adjectiveAssociations) > 1: phraseDomains.append(
        [u"=ADJECTIVE", u"=ADJECTIVE", u"=OBJECT"]
    )
    domain = random.choice(phraseDomains)

    print "Building sentence..."
    # Decide if we want to precede the phrase with a determiner ("the", "a"), create a special domain which includes determiners to add to the phrase
    if random.randint(0, 1) == 0: 
        leaderDomains = [[u"the"]]
        if pluralizeObjects: leaderDomains.append([u"some"])
        else: leaderDomains.append([u"a"])
        sentence = random.choice(leaderDomains)
    else: sentence = []

    # Iterate through the objects in the domain and fill them in to create the phrase
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=OBJECT":
            if pluralizeObjects: sentence.append(pattern.en.pluralize(word))
            else: sentence.append(word)
        elif slot == u"=ADJECTIVE": sentence.append(choose_association(adjectiveAssociations)['target'])
    
    return sentence

def finalize_reply(reply):
    print "Finalizing reply..."
    # Fix positions of punctuation, refer to Ellie and Alex as mom and dad
    for count, word in enumerate(reply):
        if u"sharkthemepark" in word: reply[count] = u"mom"
        elif u"nosiron" in word: reply[count] = u"dad"
        elif word in [u",", u".", u"!", u"?"]:
            reply[count - 1] += word
            del reply[count]
        if word == []: del reply[count]
            
    return ' '.join(reply)
    
print generate_sentence([[[u'hi', u'UH', u'O', u'O'], [u'emma', u'NNP', u'B-NP', u'O'], [u'!', u'.', u'O', u'O']], [[u'sharkthemepark', 'NNP', u'B-NP', u'NP-SBJ-1'], [u'hope', u'VBP', u'B-VP', u'VP-1'], [u'emma', 'NNP', u'B-NP', u'NP-OBJ-1*NP-SBJ-2'], [u'be', u'VBP', u'B-VP', u'VP-2'], [u'do', u'VBG', u'I-VP', u'VP-2'], [u'well', u'RB', u'B-ADVP', u'O'], [u'.', u'.', u'O', u'O']], [[u'sharkthemepark', 'NNP', u'B-NP', u'NP-SBJ-1'], [u'like', u'VBP', u'B-VP', u'VP-1'], [u'dog', u'NNS', u'B-NP', u'NP-OBJ-1'], [u'because', u'IN', u'B-PP', u'O'], [u'dog', u'NNS', u'B-NP', u'NP-OBJ-1'], [u'be', u'VBP', u'B-VP', u'VP-2'], [u'gay', u'JJ', u'B-ADJP', u'O'], [u'.', u'.', u'O', u'O']]], 0.2983478546283, u"sharkthemepark",)