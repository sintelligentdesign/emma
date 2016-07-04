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

def generate_sentence(tokenizedMessage, mood, askerIntents=['DECLARATIVE'], intentDetails=[], asker=""):
    # todo: optimize sentence generation
    print "Creating reply..."
    for intent in askerIntents:
        if intent == 'INTERROGATIVE':
            print Fore.YELLOW + "Question detected. Answering..."
            reply = answer_question(intentDetails)
            return finalize_reply(reply)

    print "Determining important words..."
    importantWords = []
    message = []
    for sentence in tokenizedMessage:
        for word in sentence:
            message.append(word[0])
            if word[1] in utilities.nounCodes and word[3] and word[0] not in importantWords:
                importantWords.append(word[0])

    # Find associations
    # Association package (information about bundle and the bundle itself) > Association bundle (a collection of words and their corresponding association groups) > Association group (a collection of associations without their word) > association (association type, target, weight)
    print "Creating association bundles..."
    associationBundle, unknownWords = bundle_associations(importantWords)

    if len(associationBundle) < 3:
        print Fore.YELLOW + "The number of associations in the primary bundle is small. Adding associations from common sense halo..."
        print "Creating common sense halo..."
        halo = make_halo(make_halo(importantWords))
        associationBundle, unknownWords = bundle_associations(halo)

    # Create packages which include the association package and information about its contents so that the generator knows what domains can be used
    print "Packaging association bundles and related information..."
    associationPackage = make_association_package(associationBundle, asker)

    # Generate the reply
    reply = build_reply(associationPackage, mood, askerIntents, unknownWords)
    return finalize_reply(reply)

def answer_question(intentDetails):
    if intentDetails[0] == "whatBe":
        with connection:
            cursor.execute("SELECT * FROM associationmodel WHERE word = \'%s\' OR target = \'%s\' AND association_type != \'HAS-OBJECT\';" % (intentDetails[1], intentDetails[1]))
            featureAssociations = cursor.fetchall()
            cursor.execute("SELECT * FROM associationmodel WHERE word = \'%s\' OR target = \'%s\' AND association_type != \'HAS-OBJECT\';" % (intentDetails[2], intentDetails[2]))
            targetAssociations = cursor.fetchall()

            print featureAssociations
            print targetAssociations
        
        if featureAssociations and targetAssociations:
            possibleAnswers = []
            for featureAssociation in featureAssociations:
                for targetAssociation in targetAssociations:
                    if featureAssociation[0] in [targetAssociation[0], targetAssociation[2]]: possibleAnswers.append((featureAssociation[0], featureAssociation[3] + targetAssociation[3]))
                    elif featureAssociation[2] in [targetAssociation[0], targetAssociation[2]]: possibleAnswers.append((featureAssociation[2], featureAssociation[3] + targetAssociation[3]))
                    elif targetAssociation[0] in [featureAssociation[0], featureAssociation[2]]: possibleAnswers.append((targetAssociation[0], featureAssociation[3] + targetAssociation[3]))
                    elif targetAssociation[2] in [featureAssociation[0], featureAssociation[2]]: possibleAnswers.append((targetAssociation[2], featureAssociation[3] + targetAssociation[3]))
            print possibleAnswers

            # todo: use weighted die roll
            answer = random.choice(possibleAnswers)[0]
            
            # todo: make the output prettier
            reply = [intentDetails[1], u"of", intentDetails[2], u"is", answer]
            return reply

def make_halo(words):
    halo = []
    for word in words:
        with connection:
            cursor.execute("SELECT target FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.target = dictionary.word WHERE associationmodel.word = \"%s\" AND part_of_speech IN (\'NN\', \'NNS\', \'NNP\', \'NNPS\');" % re.escape(word))
            for fetchedWord in cursor.fetchall(): halo.extend(fetchedWord)
    return halo

def bundle_associations(words):
    associationBundle = []
    unknownWords = []
    for word in words:
        print Fore.GREEN + "Finding associations for \'%s\'..." % word
        with connection:
            cursor.execute("SELECT * FROM associationmodel WHERE word = \"%s\";" % re.escape(word))
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
        else: unknownWords.append(word)
    return associationBundle, unknownWords

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
            else: 
                # todo: This is a bad fix and we should find a better thing to do with objects of things
                if association['type'] == "HAS-OBJECT":
                    print Fore.YELLOW + "Using HAS-OBJECT in place of HAS-ABILITY-TO for \'%s\'" % associationGroup[0]
                    hasHasAbilityTo = True
                    association['type'] = "HAS-ABILITY-TO"
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

def determine_valid_intents(associationPackage, unknownWords):
    # This function doesn't include interrogatives or greetings, since those are Association Bundle-specific
    validIntents = {}
    for associationBundle in associationPackage[1]:
        intents = []
        if associationBundle['hasHasProperty']: intents.append('DECLARATIVE')
        if associationPackage[0]['numObjects'] >= 2 and 'DECLARATIVE' in intents: intents.append('COMPARATIVE')
        if associationBundle['hasHasAbilityTo']: intents.append('IMPERATIVE')
        if associationPackage[0]['numObjects'] >= 1: intents.append('PHRASE')
        validIntents[associationBundle['word']] = intents
    for word in unknownWords: validIntents[word] = 'INTERROGATIVE'
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

def build_reply(associationPackage, mood, askerIntents, unknownWords):
    reply = []
    sentencesToGenerate = random.randint(1, 3)

    usedWords = []

    # If conditions are right, add a greeting
    if mood >= 0.1 and 'GREETING' in askerIntents and associationPackage[0]['asker'] != "": reply = make_greeting(associationPackage[0]['asker']) + [u"!"]
  
    for sentenceIterator in range(0, sentencesToGenerate):
        print Fore.MAGENTA + "Generating sentence %d of %d..." % (sentenceIterator + 1, sentencesToGenerate)

        # Create list of words and intents to choose from
        validIntents = determine_valid_intents(associationPackage, unknownWords)
        if console['verboseLogging']: print "Valid intents: " + str(validIntents)

        word = random.choice(validIntents.keys())
        intent = random.choice(validIntents[word])

        # todo: figure out a way to decrease the likelihood of words in usedWords being used again
        usedWords.append(word)

        for associationBundle in associationPackage[1]:
            if associationBundle['word'] == word: associationBundle = associationBundle

        # Decide whether to make objects in the sentence plural
        if random.randint(0, 1) == 0: pluralizeObjects = True
        else: pluralizeObjects = False

        if console['verboseLogging']: print "Intent: " + intent

        # Fill in our chosen intent
        elif intent == 'PHRASE': sentence = make_phrase(associationBundle['word'], associationBundle['associations'], pluralizeObjects) + [u"."]

        elif intent == 'DECLARATIVE':
            bundleInfo = {'hasHas': associationBundle['hasHas'], 'hasIsA': associationBundle['hasIsA'], 'hasHasProperty': associationBundle['hasHasProperty'], 'hasHasAbilityTo': associationBundle['hasHasAbilityTo']}
            sentence = make_declarative(associationBundle['word'], associationBundle['associations'], pluralizeObjects, bundleInfo, mood) + [u"."]

        elif intent == 'COMPARATIVE':
            wordsToCompare = []
            for word in validIntents.keys():
                if 'COMPARATIVE' in validIntents[word]:
                    wordsToCompare.append(word)
            comparisonChoices = []
            for word in wordsToCompare:
                for associationBundle in associationPackage[1]:
                    if associationBundle['word'] == word: comparisonChoices.append(associationBundle)
            sentence = make_comparative(associationBundle, random.choice(comparisonChoices), pluralizeObjects, mood) + [u"."]

        elif intent == 'IMPERATIVE':
            bundleInfo = {'hasHas': associationBundle['hasHas'], 'hasIsA': associationBundle['hasIsA'], 'hasHasProperty': associationBundle['hasHasProperty'], 'hasHasAbilityTo': associationBundle['hasHasAbilityTo']}
            sentence = make_imperative(associationBundle['word'], associationBundle['associations'], pluralizeObjects, mood) + [u"."]

        elif intent == 'INTERROGATIVE':
            sentence = make_interrogative(word, pluralizeObjects) + [u"?"]
            
        sentence[0] = sentence[0][0].upper() + sentence[0][1:]
        print sentence
        reply.extend(sentence)
    
    return reply

def make_greeting(asker):
    if console['verboseLogging']: print "Generating a greeting..."
    greetingDomains = [
        [u"Hi", asker], 
        [u"Hello", asker]
    ]
    return random.choice(greetingDomains)

def make_comparative(associationBundle, comparisonBundle, pluralizeObjects, mood):
    if console['verboseLogging']: print "Generating a comparative statement for \'%s\' and \'%s\'..." % (associationBundle['word'], comparisonBundle['word'])

    if console['verboseLogging']: print "Choosing domain..."
    comparativeDomains = [
        [u"=DECLARATIVE", u"like", u"=COMPARISON"],
        [u"=DECLARATIVE", u",", u"and", u"=COMPARISON"],
        [u"=DECLARATIVE", u",", u"but", u"=COMPARISON"]
    ]
    domain = random.choice(comparativeDomains)

    if console['verboseLogging']: print "Building comparative statement..."
    sentence = []
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=DECLARATIVE":
            bundleInfo = {'hasHas': associationBundle['hasHas'], 'hasIsA': associationBundle['hasIsA'], 'hasHasProperty': associationBundle['hasHasProperty'], 'hasHasAbilityTo': associationBundle['hasHasAbilityTo']}
            sentence.extend(make_declarative(associationBundle['word'], associationBundle['associations'], pluralizeObjects, bundleInfo, mood))
        elif slot == u"=COMPARISON":
            bundleInfo = {'hasHas': comparisonBundle['hasHas'], 'hasIsA': comparisonBundle['hasIsA'], 'hasHasProperty': comparisonBundle['hasHasProperty'], 'hasHasAbilityTo': associationBundle['hasHasAbilityTo']}
            sentence.extend(make_declarative(comparisonBundle['word'], comparisonBundle['associations'], pluralizeObjects, bundleInfo, mood))
        else: sentence.append(slot)

    return sentence

def make_declarative(word, associationGroup, pluralizeObjects, bundleInfo, mood):
    if console['verboseLogging']: print "Generating a declarative statement for \'%s\'..." % word
    
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

    if console['verboseLogging']: print "Choosing domain..."
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

    if console['verboseLogging']: print "Building declarative statement..."
    sentence = []
    # Iterate through the objects in the domain and fill them in to create the declarative statement
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=OBJECT": sentence.extend(make_phrase(word, associationGroup, pluralizeObjects))
        elif slot == u"=ADJECTIVE": sentence.append(choose_association(ispropertyofAssociations)['target'])
        elif slot == u"=ACTION": sentence.append(make_imperative(word, associationGroup, pluralizeObjects, mood))
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

def make_imperative(word, associationGroup, pluralizeObjects, mood):
    if console['verboseLogging']: print "Generating an imperative statement for \'%s\'..." % word

    if console['verboseLogging']: print "Looking for verb associations..."
    verbAssociations = []
    for association in associationGroup:
        if association['type'] == "HAS-ABILITY-TO": verbAssociations.append(association)

    if len(verbAssociations) == 0: print Fore.YELLOW + "No verbs available for \'%s\'!" % word

    if console['verboseLogging']: print "Choosing domain..."
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
    
    if console['verboseLogging']: print "Building imperative statement..."
    if mood > 0.4: sentence = [u"please"]
    else: sentence = []
    for count, slot in enumerate(sentence):
        print sentence + domain[count:]
        if slot == "=OBJECT": sentence.extend(make_phrase(word, associationGroup, pluralizeObjects))
        elif slot == "=VERB": sentence.append(choose_association(verbAssociations)['target'])
        else: sentence.append(slot)

    return sentence

def make_interrogative(word, pluralizeObjects):
    if console['verboseLogging']: print "Generating an interrogative phrase for \'%s\'..." % word

    if console['verboseLogging']: print "Choosing domain..."
    interrogativeDomains = [
        [u"what\'s", u"=WORD"]
    ]
    if pluralizeObjects: interrogativeDomains.append(
        [u"what", u"are", u"=WORD"]
    )
    else: interrogativeDomains.append(
        [u"what", u"is", u"=WORD"]
    )
    domain = random.choice(interrogativeDomains)

    if console['verboseLogging']: print "Building interrogative phrase..."
    sentence = []
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=WORD":
            if pluralizeObjects: sentence.append(pattern.en.pluralize(word))
            else: sentence.append(word)
        else: sentence.append(slot)

    return sentence

def make_phrase(word, associationGroup, pluralizeObjects):
    if console['verboseLogging']: print "Generating a phrase for \'%s\'..." % word
    
    if console['verboseLogging']: print "Looking for adjective associations..."
    adjectiveAssociations = []
    for association in associationGroup:
        if association['type'] == "HAS-PROPERTY":
            with connection:
                cursor.execute("SELECT * FROM dictionary WHERE word = \'%s\' AND part_of_speech IN (\'JJ\', \'JJR\', \'JJS\');" % association['target'])
                if cursor.fetchall() != []: adjectiveAssociations.append(association)
    
    if len(adjectiveAssociations) == 0: 
        if console['verboseLogging']: print Fore.YELLOW + "No adjectives available for \'%s\'!" % word

    if console['verboseLogging']: print "Choosing domain..."
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

    if console['verboseLogging']: print "Building phrase..."
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