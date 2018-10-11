import os
import sys
import requests
import re
from bs4 import BeautifulSoup

ACCESS_TOKEN = "NO_AUTH"
GLOSSARY_FILE_ID = "157DEoAx2aFRcJFXe2ce1yhEttiGqFSbhVQou5zKX7CI"
htmlPattern = r'<.*?>'
htmlChecker = re.compile(htmlPattern)

def escapeHTML(s):
  return re.sub(htmlChecker, '', s)

def createTooltip(term, definition):
  return '<attr data-toggle="tooltip" data-placement="bottom" title="'+definition+'">'+term+'</attr>'

def define(text, glossary):
  for term in glossary:
    pos = text.find(term)
    while pos != -1:
      text = text[:pos] + createTooltip(term, glossary[term]) + text[pos+len(term):]


def get_glossary_from_google():
  url = "https://www.googleapis.com/drive/v3/files/"+GLOSSARY_FILE_ID+"/export?mimeType=text%2Fcsv"
  headers = {'Authorization': 'Bearer '+ACCESS_TOKEN}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "response:",  r.text
    print "auth failed. update access token"
  else:
    rawdata = r.text.encode('utf-8')
    lines = rawdata.split()[1:] # throw out the first line
    glossary = {}
    for line in lines:
      divider = line.find(',')
      word = escapeHTML(line[:divider])
      definition = escapeHTML(line[divider+1:])
      glossary[word] = definition
    return glossary

if __name__ == '__main__':

  if len(sys.argv == 2):
    ACCESS_TOKEN = sys.argv[1]
    glossary = get_glossary_from_google()

    for root, dirs, files in os.walk("export/Pages"):
      for file in files:
        if file.endswith('.html'):
          text = open(root+"/"+file, 'r').read()
          text = define(text, glossary)
          f = open(root+"/"+file, 'w')
          f.write(text)
          f.close()

    glossaryText = open('glossary.html', 'r').read()
    glossarySoup = BeautifulSoup(glossaryText, 'lxml')

    dl = glossarySoup.dl
    dl.contents = []
    for term in glossary:
      termtag = glossarySoup.new_tag('dt')
      termtag['class'] = ['col-sm-3']
      termtag.append(term)
      dl.append(termtag)
      deftag = glossarySoup.new_tag('dd')
      deftag['class'] = ['col-sm-9']
      deftag.append(glossary[term])
      dl.append(deftag)

    glossaryHandle = open('glossary.html', 'lmxl')
    glossaryHandle.write(glossarySoup.prettify().encode('utf-8'))
    glossaryHandle.close()

    sys.stdout.write("complete")