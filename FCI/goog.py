# Normalized Google Distance

import urllib.request
import sys
import math
import json

path = "https://www.googleapis.com/customsearch/v1?"
api = "key=<your key>"
searchengine = "cx=<your search engine>"

alreadyFetched = {}

def totalResults(word1):
    if (word1 in alreadyFetched.keys()):
        return alreadyFetched[word1]
    qstring = path + api + "&" + searchengine + "&" + "q="+word1 
    contents = urllib.request.urlopen(qstring).read()
    c = json.loads(contents.decode('utf8'))
    totalResults = c["searchInformation"]["totalResults"]
    alreadyFetched[word1] = totalResults
    print("Total results:",word1, float(totalResults))
    return float(totalResults)

def Kconditional(word1, word2):
    return K(str(word1) + "+" + str(word2)) / K(word2)

def K(word):
    freq = float(totalResults(word))/(2 * (10**12))
    if freq == 0:
        freq = 0.000001
    return math.log(1/freq, 2)

def ngd(word1, word2):
    return max(Kconditional(word1, word2), Kconditional(word2, word1)) / max(K(word1), K(word2))

if __name__ == "__main__":
    first = sys.argv[1]
    second = sys.argv[2]
    print("NGD between (%s and %s) is: %f"%(first, second, ngd(first, second)))