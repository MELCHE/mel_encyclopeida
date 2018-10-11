import sys
import os
from bs4 import BeautifulSoup
from bs4 import NavigableString
from pathlib import Path
import re
import string
import random

BASE_URL = "http://encyclopedia.che.engin.umich.edu/"

def getTopicDirectory(path):
  p = Path(path)
  return p.parents[1].name

def prettifyDirectoryName(directory):
  return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', directory)

def randomIdentifier():
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

if __name__ == '__main__':
  exportPath = Path("export/Pages")
  exportPathString = exportPath.as_posix()
  exportPrefix = exportPathString[:exportPathString.find('/')]
  # map from topic directory to list of file paths that are inside the directory
  containedFilePaths = {}

  # map from file name to enclosing topic directory
  containingDirs = {}

  for root, dirs, files in os.walk(exportPath.as_posix()):
    if 0 < len(files):
      referenceableRoot = root[root.find('/')+1:]
      for file in files:
        if file in ["menu.html", "menu.json"] or file.startswith(".") or file.endswith('.png') or file.endswith('.jpeg'):
          continue
        fullyQualifiedPath = os.path.join(referenceableRoot, file)
        topicDirectory = getTopicDirectory(fullyQualifiedPath)

        containingDirs[fullyQualifiedPath] = topicDirectory
        if topicDirectory not in containedFilePaths:
          containedFilePaths[topicDirectory] = []
        containedFilePaths[topicDirectory].append(fullyQualifiedPath)

  for file in containingDirs:
    # create a bs instance
    handle = open(exportPrefix+"/"+file, 'r')
    file_contents = handle.read()
    handle.close()
    DOM = BeautifulSoup(file_contents, 'lxml')

    # create the reference link
    properDirectoryTitle = prettifyDirectoryName(containingDirs[file])
    backlink = DOM.find('span', class_='back-link')
    backlink.contents = []
    backlink.contents.append(NavigableString(properDirectoryTitle))

    # build a table of contents
    headings = DOM.find('div', id='article-content').find_all(re.compile(r'h[123456]'))
    tblOfContents = DOM.find('div', class_='table-of-contents-links')
    tblOfContents.contents = []
    for heading in headings:
      identifier = randomIdentifier();
      heading['id'] = identifier
      link = DOM.new_tag('a', href='#'+identifier)
      if heading.string != None:
        title = unicode(heading.string)
        link.append(title)
        link['class'] = [heading.name+"-lvl"]
        tblOfContents.append(link)

    # add a set of links for pages
    relatedLinks = DOM.find('div', class_='related-articles-links')
    relatedLinks.contents = []
    for relatedPage in containedFilePaths[containingDirs[file]]:
      relatedPagePath = Path(relatedPage)
      linkName = prettifyDirectoryName(relatedPagePath.stem)
      linkRelativeHref = "../"+relatedPagePath.parent.name+"/"+relatedPagePath.name
      link = DOM.new_tag('a', href=linkRelativeHref)
      link.append(linkName)
      relatedLinks.append(link)

    # send output back to DOM
    writeHandle = open(exportPrefix+"/"+file, 'w')
    writeHandle.write(DOM.prettify().encode('utf-8'))
    writeHandle.close()
  sys.stdout.write("completed")
