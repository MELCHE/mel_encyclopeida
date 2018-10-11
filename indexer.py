import os
import sys
import json
from bs4 import BeautifulSoup
from Counter import Counter
from string import punctuation
from stemming.porter2 import stem

BASE_URL = 'http://encyclopedia.che.engin.umich.edu/'

def getWordsFrom(name):
  articleSoup = BeautifulSoup(open(name), 'lxml').find('div', id='article-content')
  words = []
  for i in range(1, 3):
    lists = (heading.text.split() * (3**(6-i)) for heading in articleSoup.find_all('h'+str(i)))
    for l in lists:
      words.extend(l)
  words += articleSoup.text.split()
  return words
  # return BeautifulSoup(open(name), 'lxml').find('div', id='article-content').text.split()

if __name__ == '__main__':

  # get a set of stop words
  stopwords = set(open('search/stopwords.txt').read().split())

  def wordCount(docID):
    words = getWordsFrom(documents[docID]['path'])
    words = [w.encode('utf-8').translate(None, punctuation) for w in words]
    words = map(str.lower, words)
    words = [stem(w) for w in words if not w in stopwords and w != '']
    # return the results
    return (docID, Counter(words))

  def compileInvIndex(index, counts):
    for word in counts[1]:
      if not word in index:
        index[word] = []
      index[word].append(counts[0])
      index[word].append(counts[1][word])
    return index

  def addWC(docData, docTup):
    docData[docTup[0]]['numwords'] = sum(docTup[1].values())
    return docData

  # clean out old indexes
  oldIndexFiles = os.listdir('search')
  for f in oldIndexFiles:
    if f != "stopwords.txt":
      os.remove('search/'+f)

  os.chdir('export') # work out of the export directory

  # walk the Pages directory and map URLs to docIds.
  idCounter = 0
  documents = {}

  for root, dirs, files in os.walk("Pages"):
    for f in files:
      if f.startswith('menu') or f.startswith('.'):
        continue
      filepath = root + '/' + f
      documents[idCounter] = {'path': filepath}
      idCounter += 1

  os.chdir('..') # work out of the top level directory

  counts = map(wordCount, documents)

  # build and write the inverted index
  invIndex = reduce(compileInvIndex, counts, {})
  numdocsFileHandle = open('search/numdocs', 'w')
  numdocsFileHandle.write(str(len(documents)))
  numdocsFileHandle.close()

  sortedwords = sorted(invIndex)
  letter = None
  fileHandle = None
  for word in sortedwords:
    if letter != word[0]:
      letter = word[0]
      if fileHandle != None:
        fileHandle.close()
      fileHandle = open('search/'+letter, 'w')
    fileHandle.write(word + '\t' + ' '.join(str(v) for v in invIndex[word]) + '\n')
  fileHandle.close()

  # write the dictionary mapping
  documents = reduce(addWC, counts, documents)

  docIdMappingFileHandle = open('search/docids.json', 'w')
  json.dump(documents, docIdMappingFileHandle)
  docIdMappingFileHandle.close()

  sys.stdout.write("complete")
  # total number of documents = N

  # tf = raw count of word w in document d
  # idf = N/ # of docs that contain w
  # tf*idf score helps to rank search results





