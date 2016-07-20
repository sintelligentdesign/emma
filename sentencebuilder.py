# Name:             Sentence Generator
# Description:      Generates sentences based on what Emma knows about English and the world
# Section:          REPLY
import random
import re

import pattern.en
import sqlite3 as sql
import pattern.en
from colorama import init, Fore
init(autoreset = True)

import utilities
from config import console, files

connection = sql.connect(files['dbPath'])
cursor = connection.cursor()

mood = 0

def generate_sentence(tokenizedMessage, moodAvg, askerIntents=[{'declarative': True, 'interrogative': False, 'greeting': False}], asker=""):
    global mood
    mood = moodAvg
    print "Creating reply..."

    print "Determining important words..."
    importantWords = []
    message = []
    for sentence in tokenizedMessage:
        for word in sentence:
            message.append(word[0])
            if word[1] in utilities.nounCodes and word[3] and word[0] not in importantWords: importantWords.append(word[0])
    if len(importantWords) == 0: 
        # Fail state
        print Fore.RED + "No important words were found in the input. Sentence generation failed."
        return "%"

    # Find associations
    print "Creating association bundles..."
    associationBundle = bundle_associations(importantWords)

    '''
    if len(associationBundle) < 3:
        if len(associationBundle) == 0: print Fore.RED + "There are no associations in the primary bundle. Creating common sense halo..."
        else: print Fore.YELLOW + "The number of associations in the primary bundle is small. Creating common sense halo..."

        halo = make_halo(importantWords)
    '''

    # Create packages which include the association package and information about its contents so that the generator knows what domains can be used
    print "Packaging association bundles and related information..."
    associationPackage = make_association_package(associationBundle, asker)
    if len(associationPackage[1]) == 0: 
        # Fail state
        print Fore.RED + "There are no associations available to generate a reply. Sentence generation failed."
        return "%"

    # Disposable code to be rewritten later once we do more things with asker intents
    # todo: do more with asker intents
    hasGreeting = False
    for intent in askerIntents:
        if intent['greeting'] == True: hasGreeting = True

    # Generate the reply
    return build_reply(associationPackage, hasGreeting)

def make_halo(words):
    halo = words
    print u"Common sense halo:",
    for word in words:
        with connection:
            cursor.execute("SELECT target FROM associationmodel LEFT OUTER JOIN dictionary ON associationmodel.target = dictionary.word WHERE associationmodel.word = \"%s\" AND part_of_speech IN (\'NN\', \'NNS\', \'NNP\', \'NNPS\');" % re.escape(word))
            for fetchedWord in cursor.fetchall():
                if fetchedWord[0] not in halo:
                    print(fetchedWord[0]),
                    halo.append(fetchedWord[0])
    print Fore.GREEN + u"[Done]"
    return halo

def group_associations(word):
    # Retrieves and groups the input string's associations
    associationGroup = []
    with connection:
        cursor.execute("SELECT * FROM associationmodel WHERE word = \"%s\";" % re.escape(word))
        SQLReturn = cursor.fetchall()
    if SQLReturn:
        for row in SQLReturn:
            associationGroup.append({
                'type': row[1], 
                'target': row[2], 
                'weight': row[3]
                })
    return associationGroup

def bundle_associations(words):
    associationBundle = []
    print Fore.GREEN + u"Finding associations for:",
    for word in words:
        print word,
        associationBundle.append((word, group_associations(word)))
    print Fore.GREEN + u"[Done]"
    return associationBundle
    
def make_association_package(associationBundle, asker):
    associationPackage = []
    for associationGroup in associationBundle:
        hasHas = False
        hasIsA = False
        hasHasProperty = False
        hasHasAbilityTo = False
        for association in associationGroup[1]:
            if association['type'] == "HAS": hasHas = True
            if association['type'] == "IS-A": hasIsA = True
            if association['type'] == "HAS-PROPERTY": hasHasProperty = True
            if association['type'] == "HAS-ABILITY-TO": hasHasAbilityTo = True
            # todo: what can we do with HAS-OBJECT?

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
        intents = ['PHRASE']
        if associationBundle['hasHas'] or associationBundle['hasIsA'] or associationBundle['hasHasProperty'] or associationBundle['hasHasAbilityTo']: intents.extend(['DECLARATIVE', 'COMPARATIVE'])
        if len(associationBundle['associations']) < 3 and associationBundle['word'] != associationPackage[0]['asker']: intents.append('INTERROGATIVE')
        if associationBundle['hasHasAbilityTo']: intents.append('IMPERATIVE')

        if console['verboseLogging']: print Fore.GREEN + u"Intents for \'" + associationBundle['word'] + u"\': " + u', '.join(intents)
        validIntents[associationBundle['word']] = intents
    return validIntents

def build_reply(associationPackage, hasGreeting):
    reply = []
    if associationPackage[0]['numObjects'] <= 3: sentencesToGenerate = random.randint(1, associationPackage[0]['numObjects'])
    else: sentencesToGenerate = random.randint(1, 3)

    # If conditions are right, add a greeting
    if mood >= 0.1 and hasGreeting == True and associationPackage[0]['asker'] != "": reply = make_greeting(associationPackage[0]['asker']) + [u"!"]
  
    # All words start with an equal chance (2) of being chosen for sentence generation. If the word is used, its chance of being chosen decreases by 1 each time it's used until it reaches 0
    wordList = {}
    for associationBundle in associationPackage[1]: wordList[associationBundle['word']] = 2
    
    for sentenceIterator in range(0, sentencesToGenerate):
        print Fore.MAGENTA + "Generating sentence %d of %d..." % (sentenceIterator + 1, sentencesToGenerate)

        # Choose the word to use as the seed for our sentence based on weighted random chance
        wordDistribution = []
        for word in wordList.keys(): wordDistribution.extend([word] * wordList[word])
        word = random.choice(wordDistribution)
        wordList[word] -= 1     # Decrease the chance of this word being chosen again
        print Fore.MAGENTA + "Sentence subject: \'%s\'" % word

        # Create list intents to choose from, and choose an intent from it
        print "Determining valid intents for words in association package..."
        validIntents = determine_valid_intents(associationPackage)
        intent = random.choice(validIntents[word])
        print Fore.MAGENTA + "Sentence intent: \'%s\'" % intent

        # Retrieve our chosen word's association group
        for associationGroupIter in associationPackage[1]:
            if associationGroupIter['word'] == word: associationGroup = associationGroupIter

        # Decide whether to make objects in the sentence plural
        # todo: check dictionary to see if the word is plural or singular so that we don't pluralize plurals or vice versa
        global pluralizeObjects
        if random.randint(0, 1) == 0: pluralizeObjects = True
        else: pluralizeObjects = False

        # Decide how to proceed with sentence generation based on our intent
        if intent == 'PHRASE': sentence = make_phrase(associationGroup) + [u"."]
        elif intent == 'DECLARATIVE': sentence = make_declarative(associationGroup) + [u"."]
        elif intent == 'IMPERATIVE': sentence = make_imperative(associationGroup) + [u"."]
        elif intent == 'INTERROGATIVE': sentence = make_interrogative(word) + [u"?"]
        elif intent == 'COMPARATIVE':
            # Choose a word to compare our seed word with, similarly to how we chose a seed word for our sentence
            comparisonCandidates = []
            for word in validIntents.keys():
                if 'COMPARATIVE' in validIntents[word]: comparisonCandidates.append(word)

            comparisonDistribution = []
            for word in wordList.keys(): comparisonDistribution.extend([word] * wordList[word])
            comparison = random.choice(comparisonDistribution)
            wordList[comparison] -= 1       # Decrease the chance of the compared word being chosen again

            for associationGroup in associationPackage[1]:
                if associationGroup['word'] == comparison: comparisonGroup = associationGroup
            sentence = make_comparative(associationGroup, comparisonGroup) + [u"."]
            
        print sentence
        reply.extend(sentence)
    
    print "Finalizing reply..."
    return finalize_reply(reply)

def choose_association(associationGroup):
    dieSeed = 0
    for association in associationGroup: dieSeed += association['weight']
    dieResult = random.uniform(0, dieSeed)

    for association in associationGroup:
        dieResult -= association['weight']
        if dieResult <= 0: return association

def make_greeting(asker):
    if console['verboseLogging']: print "Generating a greeting..."
    greetingDomains = [
        [u"Hi", asker], 
        [u"Hello", asker]
    ]
    return random.choice(greetingDomains)

def make_comparative(associationGroup, comparisonGroup):
    if console['verboseLogging']: print "Generating a comparative statement for \'%s\' and \'%s\'..." % (associationGroup['word'], comparisonGroup['word'])

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
        if slot == u"=DECLARATIVE": sentence.extend(make_declarative(associationGroup))
        elif slot == u"=COMPARISON": sentence.extend(make_declarative(comparisonGroup))
        else: sentence.append(slot)

    return sentence

def make_declarative(associationGroup):
    if console['verboseLogging']: print "Generating a declarative statement for \'%s\'..." % associationGroup['word']
    
    # Gather information about what associations we have to help us decide what domains we're allowed to use
    hasAssociations = []
    isaAssociations = []
    haspropertyAssociations = []
    hasabilitytoAssociations = []
    for association in associationGroup['associations']:
        if association['type'] == "HAS": hasAssociations.append(association)
        if association['type'] == "IS-A": isaAssociations.append(association)
        if association['type'] == "HAS-PROPERTY": haspropertyAssociations.append(association)
        if association['type'] == "HAS-ABILITY-TO": hasabilitytoAssociations.append(association)

    if console['verboseLogging']: print "Choosing domain..."
    declarativeDomains = []
    if associationGroup['hasHasProperty']: declarativeDomains.extend([
        [u"=PHRASE", u"=ISARE", u"=ADJECTIVE"]
    ])
    if len(haspropertyAssociations) > 1: declarativeDomains.append(
        [u"=PHRASE", u"=ISARE", u"=ADJECTIVE", u"and", u"=ADJECTIVE"]
    )
    if associationGroup['hasHasAbilityTo']: declarativeDomains.extend([
        [u"=PHRASE", u"=VERB"],
        [u"=PHRASE", u"can", u"=VERB"]
    ])
    if hasAssociations != []: declarativeDomains.append(
        [u"=PHRASE", u"=HAVEHAS", u"=OBJ-HAS"]
    )
    if isaAssociations != []: declarativeDomains.append(
        [u"=PHRASE", u"=ISARE", u"=OBJ-IS-A"]
    )
    domain = random.choice(declarativeDomains)

    if console['verboseLogging']: print "Building declarative statement..."
    sentence = []
    # Iterate through the objects in the domain and fill them in to create the declarative statement
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=PHRASE": sentence.extend(make_phrase(associationGroup))
        elif slot == u"=ADJECTIVE": sentence.append(choose_association(haspropertyAssociations)['target'])
        elif slot == u"=VERB": sentence.append(choose_association(hasabilitytoAssociations)['target'])       #todo: add "how" ("the snake moved (how?) quickly")
        elif slot == u"=OBJ-HAS": sentence.append(choose_association(hasAssociations)['target'])
        elif slot == u"=OBJ-IS-A": sentence.append(choose_association(isaAssociations)['target'])
        elif slot == u"=ISARE":
            if pluralizeObjects: sentence.append(u"are")
            else: sentence.append(u"is")
        elif slot == u"=HAVEHAS":
            if pluralizeObjects: sentence.append(u"have")
            else: sentence.append(u"has")
        else: sentence.append(slot)

    return sentence

def make_imperative(associationGroup):
    if console['verboseLogging']: print "Generating an imperative statement for \'%s\'..." % associationGroup['word']

    verbAssociations = []
    for association in associationGroup['associations']:
        if association['type'] == "HAS-ABILITY-TO": verbAssociations.append(association)

    if console['verboseLogging']: print "Choosing domain..."
    imperativeDomains = [
        [u"=VERB", u"=PHRASE"]
    ]
    if mood > 0: imperativeDomains.append(
        [u"always", u"=VERB", u"=PHRASE"]
    )
    else: imperativeDomains.append(
        [u"never", u"=VERB", u"=PHRASE"]
    )
    if not pluralizeObjects: imperativeDomains.append(
        [u"=VERB", u"=PHRASE"]
    )
    # todo: new domain: VERB a/an/the OBJECT with (its THING OBJECT HAS / a/an/the OTHER OBJECT)
    domain = random.choice(imperativeDomains)
    
    if console['verboseLogging']: print "Building imperative statement..."
    sentence = []
    if mood > 0.4: 
        if random.randint(0, 1) == 0: sentence = [u"please"]

    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == "=PHRASE": sentence.extend(make_phrase(associationGroup))
        elif slot == "=VERB": sentence.append(choose_association(verbAssociations)['target'])
        else: sentence.append(slot)

    return sentence

def make_interrogative(word):
    if console['verboseLogging']: print "Generating an interrogative phrase for \'%s\'..." % word

    if console['verboseLogging']: print "Choosing domain..."
    interrogativeDomains = [
        [u"what\'s", u"=WORD"]
    ]
    if pluralizeObjects: interrogativeDomains.append(
        [u"what", u"are", u"=WORD"]
    )
    else: interrogativeDomains.extend([
        [u"what", u"is", u"=WORD"],
        [u"what", u"is", u"a", u"=WORD"]
    ])
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

def make_phrase(associationGroup):
    if console['verboseLogging']: print "Generating a phrase for \'%s\'..." % associationGroup['word']
    
    if console['verboseLogging']: print "Looking for adjective associations..."
    adjectiveAssociations = []
    for association in associationGroup['associations']:
        if association['type'] == "HAS-PROPERTY": adjectiveAssociations.append(association)

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
    # Decide if we want to precede the phrase with a determiner ("the", "a")
    if random.randint(0, 1) == 0: 
        determiners = [[u"the"]]
        if pluralizeObjects: determiners.extend([[u"some"], [u"many"]])
        else: determiners.append([u"a"])
        sentence = random.choice(determiners)
    else: sentence = []

    # Iterate through the objects in the domain and fill them in to create the phrase
    for count, slot in enumerate(domain):
        print sentence + domain[count:]
        if slot == u"=OBJECT":
            if pluralizeObjects: sentence.append(pattern.en.pluralize(associationGroup['word']))
            else: sentence.append(associationGroup['word'])
        elif slot == u"=ADJECTIVE": sentence.append(choose_association(adjectiveAssociations)['target'])
    
    return sentence

def finalize_reply(reply):
    splitReply = pattern.en.parse(' '.join(reply), True, True, False, False, True).split()
    tokenizedReply = []
    for sentence in splitReply: tokenizedReply.extend(sentence)     # Fix some pattern.en formatting stuff
    
    lastUsedNouns = []
    for count, word in enumerate(tokenizedReply):
        # If we repeat proper nouns, refer back to them with "they"
        if word[1] in utilities.nounCodes:
            if tokenizedReply[count - 1][0] in [u".", u"!", u"?", u"and", u"but"]:
                if word[2] in lastUsedNouns[:2] and tokenizedReply[count + 1][1] != u".":
                    tokenizedReply[count][0] = u"they"
            lastUsedNouns.append(word[2])

        # Refer to Ellie and Alex as mom and dad
        if u"sharkthemepark" in word[0]: tokenizedReply[count][0] = u"mom"
        elif u"nosiron" in word[0]: tokenizedReply[count][0] = u"dad"

    reply = []
    for word in tokenizedReply:
        reply.append(word[0])
    
    # Correct positions of punctuation, capitalize first letter of first word in new sentences
    reply[0] = reply[0][0].upper() + reply[0][1:]
    for count, word in enumerate(reply):
        if word in [u".", u",", u"!", u"?"]:
            reply[count - 1] += word
            if count + 1 != len(reply):
                reply[count + 1] = reply[count + 1][0].upper() + reply[count + 1][1:]
        elif word == u"\'s":
            reply[count - 1] += word
    
    reply[:] = [word for word in reply if word not in [u".", u",", u"!", u"?", u"\'s"]]

    return ' '.join(reply)