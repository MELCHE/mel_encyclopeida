import sys
import json
import re
import math
from string import punctuation
from Counter import Counter
from bs4 import BeautifulSoup
from pathlib import Path
from stemming.porter2 import stem

def prettifyDirectoryName(directory):
  return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', directory)

def norm(components):
  return math.sqrt(sum([c**2 for c in components]))

def dotprod(v1, v2):
  return sum([v1[i]*v2[i] for i in range(len(v1))])

def cosineSim(v1, v2, normv1):
  return dotprod(v1, v2) / (normv1 * norm(v2))

def rankOrder(doc1, doc2):
  diff = doc1[1] - doc2[1]
  if diff < 0:
    return 1
  elif 0 < diff:
    return -1
  else:
    return 0

def segmentOrder(seg1, seg2):
  return seg1[0] - seg2[0]

def parseDocIdAndFrequencyList(l):
  tupleList = []
  for i in range(0, len(l), 2):
    tupleList.append((l[i], l[i+1]))
  return tupleList

def inBetween(num, rng):
  return rng[0] <= num and num <= rng[1]

def mergeSegments(segments):
  if len(segments) < 2:
    return segments
  i = 0
  while i < len(segments) - 1:
    if segments[i][0] < 0:
      segments[i] = (segments[i][0], segments[i][1])
    if inBetween(segments[i][1], segments[i+1]):
      segments[i] = (segments[i][0], segments[i+1][1])
      segments[i+1] = (segments[i][0], segments[i+1][1])
    i += 1

  return sorted(list(set(segments)), cmp=segmentOrder)

def annotateInstancesOf(query, text):
  segments = []
  for word in query:
    for match in re.finditer(word, text):
      start = match.start() - 20
      while 0 < start and not text[start].isspace():
        start -= 1
      end = match.end() + 20
      while end < len(text) and not text[end].isspace():
        end += 1
      segments.append((start, end))

  segments = mergeSegments(sorted(segments, cmp=segmentOrder))
  passages = [text[seg[0]:seg[1]] for seg in segments]

  for word in query:
    for i in range(len(passages)):
      passages[i] = passages[i].replace(word, '<b>'+word+'</b>')
      passages[i] = passages[i].strip()

  highlights = '...'.join(passages)
  if 240 < len(highlights):
    index = 240
    while index < len(highlights) and not highlights[index].isspace():
      index += 1
    highlights = highlights[:index]
  return highlights


if __name__ == '__main__':

  # assert that there are enough arguments
  if 2 != len(sys.argv):
    exit(1)

  # grab stopwords
  stopwords = set(open('search/stopwords.txt').read().split())

  # grab the query string
  rawQuery = json.loads(sys.argv[1])
  query = [w.encode('utf-8').translate(None, punctuation).lower().strip() for w in rawQuery if w != ""]
  query = [stem(w) for w in query if not w in stopwords]
  query.sort()

  if len(query) == 0:
    exit(1)

  # pull the doc IDs
  documents = json.loads(open('search/docids.json').read())
  documentsKeys = documents.keys()
  for key in documentsKeys:
    intVal = int(key)
    documents[intVal] = documents[key]
    del documents[key]

  # number of documents
  N = int(open('search/numdocs').read())

  # grab the necessary files
  relevantIndexFileNames = set([w[0] for w in query])
  relevantInvIndex = {}
  for letter in relevantIndexFileNames:
    contents = None
    try:
      contents = open('search/'+letter).read().split('\n')
    except IOError:
      # if there are no files with that letter, just skip instead of throwing error
      for word in query:
        if word[0] == letter:
          relevantInvIndex[word] = []
      continue
    for line in contents:
      if len(line) == 0:
        continue
      word, data = line.split('\t')
      if not word in relevantInvIndex:
        relevantInvIndex[word] = []
      relevantInvIndex[word] += parseDocIdAndFrequencyList([int(x) for x in data.split()])

  for word in query:
    if not word in relevantInvIndex:
      relevantInvIndex[word] = []

  # score the query
  queryCounts = Counter(query)
  gen = ((word, (float(queryCounts[word]) / queryCounts.most_common(1)[0][1])) for word in queryCounts)
  queryTFs = dict(gen)
  query = list(set(query)) # remove duplicates and re-sort
  query.sort()
  gen = ((w, math.log(float(N+1) / (len(relevantInvIndex[w]) + 1))) for w in query)
  queryIDFs = dict(gen)
  queryScores = [queryTFs[w] * queryIDFs[w] for w in query]
  queryNorm = norm(queryScores)

  # produce the relevant set of Doc Ids
  relevantDocIDs = set([])
  TFs = {}
  for word in query:
    matchedDocIDs = relevantInvIndex[word]
    gen = (((doc[0], word), (float(doc[1]) / documents[doc[0]]['numwords'])) for doc in matchedDocIDs)
    TFs.update(dict(gen))
    relevantDocIDs |= set([doc[0] for doc in matchedDocIDs])

  # print TFs

  # produce a dictionary of relevant DocIDs to TFs
  gen = ((docID, [TFs[(docID, word)] if (docID, word) in TFs else 0  for word in query]) for docID in relevantDocIDs)
  docTFs = dict(gen)
  gen = ((docID, [ math.log(float(N + 1) / (len(relevantInvIndex[word]) + 1)) for word in query]) for docID in relevantDocIDs)
  docIDFs = dict(gen)
  # print docTFs

  gen = ((docID, [docTFs[docID][i] * docIDFs[docID][i] for i in range(len(query))]) for docID in relevantDocIDs)
  docScores = dict(gen)
  # print docScores
  # print ""
  docRanks = [(docID, cosineSim(queryScores, docScores[docID], queryNorm)) for docID in docScores]
  # print docRanks
  docRanks = sorted(docRanks, key=lambda x: x[1])
  docRanks.reverse()
  # Get a list of Paths
  resultDocs = [documents[doc[0]]['path'] for doc in docRanks[:10]]

  # print resultDocs

  results = []

  for path in resultDocs:
    rawText = BeautifulSoup(open(path).read(), 'lxml').text
    result = {}
    result['linkhref'] = path
    result['title'] = prettifyDirectoryName(Path(path).stem)
    result['highlight'] = annotateInstancesOf(rawQuery, rawText)
    results.append(result)

  sys.stdout.write(json.dumps(results))
