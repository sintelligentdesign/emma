# Name:             Chunk Unpacker
# Description:      Takes chunks as input and turns them into parts of speech
# Section:          REPLY
import utilities

def unpack(chunkList):
    print "Getting parts of speech from generated chunks..."
    # todo: use sentence parts of speech to choose which code to use when filling in sentences
    POSList = []
    for chunk in chunkList:
        if "NP" in chunk:
            POSList.extend(["DT"] + utilities.adverbCodes + utilities.adjectiveCodes + utilities.nounCodes + ["PRP"])
        elif "PP" in chunk:
            POSList.extend(["TO", "IN"])
        elif "VP" in chunk:
            POSList.extend(utilities.adverbCodes + ["MD"] + utilities.verbCodes)
        elif "ADVP" in chunk:
            POSList.extend(utilities.adverbCodes)
        elif "ADJP" in chunk:
            POSList.extend(["CC"] + utilities.adverbCodes + utilities.adjectiveCodes)
        elif "SBAR" in chunk:
            POSList.extend(["IN"])
        elif "PRT" in chunk:
            POSList.extend(["RP"])
        elif "INTJ" in chunk:
            POSList.extend(["UH"])
    return POSList