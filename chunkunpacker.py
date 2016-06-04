# Name:             Chunk Unpacker
# Description:      Takes chunks as input and turns them into parts of speech
# Section:          REPLY
# Writes/reads:     
# Dependencies:     
# Dependency of:    

def unpack(chunkList):
    print "Getting parts of speech from generated chunks..."
    POSList = []
    for chunk in chunkList:
        if "NP" in chunk:
            POSList.extend(["DT", "RB", "JJ", "NN", "PR"])
        elif "PP" in chunk:
            POSList.extend(["TO", "IN"])
        elif "VP" in chunk:
            POSList.extend(["RB", "MD", "VB"])
        elif "ADVP" in chunk:
            POSList.extend(["RB"])
        elif "ADJP" in chunk:
            POSList.extend(["CC", "RB", "JJ"])
        elif "SBAR" in chunk:
            POSList.extend(["IN"])
        elif "PRT" in chunk:
            POSList.extend(["RP"])
        elif "INTJ" in chunk:
            POSList.extend(["UH"])
    return POSList