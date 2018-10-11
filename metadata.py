import sys
import os
import json
from bs4 import BeautifulSoup
import re
from random import shuffle

BASE_URL = "http://encyclopedia.che.engin.umich.edu/Pages/"

def prettifyDirectoryName(directory):
  return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', directory)

if __name__ == '__main__':
  if len(sys.argv) == 3:
    rootDir = sys.argv[1]
    ignorePrefix = sys.argv[2]
    metadata = []

    for root, dirs, files in os.walk(rootDir):
      if root.startswith(ignorePrefix):
        relroot = root[len(ignorePrefix):]

      for f in files:
        if 'html' in f:
          filePath = root + '/' + f
          urlPath = BASE_URL + filePath

          soup = BeautifulSoup(open(filePath, 'r').read(), 'lxml')
          article = soup.find('div', id='article-content')
          title = prettifyDirectoryName(f.split('.')[0])
          afterHeading = article.h1.next_element
          while afterHeading != None and afterHeading.name != 'p':
            afterHeading = afterHeading.next_element
          leaderText = afterHeading.text.strip()
          if 240 < len(leaderText): # don't let a leader be longer than a tweet
            leaderText = leaderText[:240]
          leaderText += '...'
          representiveImage = "http://encyclopedia.che.engin.umich.edu/Images/melicon.png"
          if article.img != None:
            representiveImage = article.img['src']
          # if there was a representative image choosen, use that instead
          if "menu.png" in files:
            representiveImage = relroot + '/menu.png'
          elif "menu.jpeg" in files:
            representiveImage = relroot + '/menu.jpeg'
          details = {
            'url': urlPath,
            'title': title,
            'leader': leaderText,
            'imgsrc': representiveImage
          }
          metadata.append(details)

    shuffle(metadata)

    # pull up the index page and add these articles
    # indexSoup = BeautifulSoup(open('index.html').read(), 'lxml')

    # indexSoup.

    handle = open('article_metadata.json', 'w')
    handle.write(json.dumps(metadata))
    handle.close()

