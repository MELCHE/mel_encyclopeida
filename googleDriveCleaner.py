from bs4 import BeautifulSoup
from bs4 import NavigableString
import sys
import re
import cssutils
import math
import urlparse
import logging
import json
cssutils.log.setLevel(logging.CRITICAL)

BASE_URL = "http://encyclopedia.che.engin.umich.edu"
videoLinkPattern = r'\s*{{\s*VIDEO:\s*http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+ ]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\s*}}\s*'
diagramLinkPattern = r'\s*{{\s*DIAGRAM:\s*(?P<src>Diagrams/[0-9]+\.[0-9]?\.?json)\s*}}\s*'
videoIDPattern = r'http[s]?://.*/(?P<ID>\S+)$'
videoLinkChecker = re.compile(videoLinkPattern)
diagramLinkChecker = re.compile(diagramLinkPattern)
videoIDChecker = re.compile(videoIDPattern)

def googleDriveCleaner(html, template):
  # soupify the inputdom
  inputDOM = BeautifulSoup(html, 'lxml')
  # soupify the outputdom
  outputDOM = BeautifulSoup(template, 'lxml')

  # unwrap all span tags from the body
  spans = inputDOM.find_all('span')
  for span in spans:
    if 'style' in span.attrs:
      styles = cssutils.parseStyle(span['style'].encode('utf-8'))
      if 'vertical-align' in styles and styles['vertical-align'] == 'super':
        span.name = 'sup'
        del span['style']
        continue
      elif 'vertical-align' in styles and styles['vertical-align'] == 'sub':
        span.name = 'sub'
        del span['style']
        continue
    span.unwrap()

  # remove styling on all tags inside the body, except for text alignment
  tags = inputDOM.body.find_all(True)
  for tag in tags:
    if 'style' in tag.attrs:
      styles = cssutils.parseStyle(tag['style'].encode('utf-8'))
      keys = styles.keys()
      for key in keys:
        if key not in ['text-align']:
          del styles[key]
      tag['style'] = styles.cssText.replace('\n', ' ').replace('\r', '')


  # convert videos from links into iframes
  anchors = inputDOM.find_all('a')
  diagramID = 0
  for anchor in anchors:
    if 'href' not in anchor.attrs:
      anchor.decompose()
      continue
    googleURL = anchor['href']
    googleURL = googleURL.replace('&amp;', '&')
    parsed = urlparse.urlparse(googleURL)[4]
    if 'q' in parsed:
      anchor['href'] = urlparse.parse_qs(urlparse.urlparse(googleURL)[4])['q'][0]

    anchor_contents = unicode(anchor.string).encode('utf-8')
    videoLinkMatch = videoLinkChecker.match(anchor_contents)
    diagramLinkMatch = diagramLinkChecker.match(anchor_contents)

    if videoLinkMatch:
      videoIDmatch = videoIDChecker.match(anchor['href'])
      videoID = videoIDmatch.group('ID')

      # create a new frame tag
      frame = inputDOM.new_tag('iframe')
      frame['src'] = anchor['href'] + '?loop=1&controls=0&disablekb=1&playlist=' + videoID
      frame['class'] = ['embed-responsive-item']
    
      # make the original tag a p
      del anchor['href']
      anchor.name = 'p'
      anchor.string = ''
      anchor['class'] = ['embed-responsive','embed-responsive-4by3']
      anchor.append(frame)

    if diagramLinkMatch:
      jsonPath = diagramLinkMatch.group('src')
      jsonText = open(jsonPath, 'r').read()
      jsonData = json.loads(jsonText)
      thisid = 'diagram_' + str(diagramID)
      jsonData['id'] = thisid
      diagramID += 1
      jsonText = json.dumps(jsonData)
      anchor.name = 'img'
      anchor['src'] = BASE_URL + '/' + jsonData['src']
      anchor['class'] = []
      anchor['class'].append('diagram')
      anchor['id'] = thisid
      anchor.string = ''
      scriptag = inputDOM.new_tag('script')
      scriptag.string = 'var ' + thisid + ' = ' + jsonText + ';'
      anchor.insert_after(scriptag);

  # convert tables into bootstrap grids
  tables = inputDOM.find_all('table')
  for table in tables:
    if table.tbody:
      table.tbody.unwrap()
    rows = table.find_all('tr')
    for row in rows:
      cells = row.find_all('td')
      totalColSpan = 0
      for cell in cells:
        totalColSpan += int(cell['colspan'])
      totalColSpan = max(totalColSpan, 1)
      colspan_alloc = 12/totalColSpan
      for cell in cells:
        grid_space = max(int(math.floor(colspan_alloc * int(cell['colspan']))), 1)
        cell.name = 'div'
        cell['class'] = ['col-xs-'+str(grid_space)]
        del cell['colspan']
        del cell['rowspan']
        del cell['style']
      row.name = 'div'
      row['class'] = ['row']
      del row['style']

    table.unwrap()

  # remove all the empty paragraphs
  paragraphs = inputDOM.find_all('p')
  for paragraph in paragraphs:
    if len(paragraph.contents) == 0:
      paragraph.decompose()

  # make all images fluid
  imgs = inputDOM.find_all('img')
  for img in imgs:
    if img.get('class') == None:
      img['class'] = []
      img['class'].append("class-not-in-image")
    img['class'].append('img-fluid')

  # transfer the new body over (leaving behind the css in style)
  outputDOM.find('div', id='article-content').contents = inputDOM.body.contents

  # collect some basic information about the article

  details = {}
  article = outputDOM.find('div', id='article-content')
  leaderText = ''
  try:
    if article.p != None:
      leaderText = article.p.text.strip()
  except AttributeError:
    pass
  if 240 < len(leaderText): # don't let a leader be longer than a tweet
    leaderText = leaderText[:240]
  leaderText += '...'
  details['leader'] = leaderText
  details['imgsrc'] = "http://encyclopedia.che.engin.umich.edu/Images/melicon.png"
  if 0 < len(imgs):
    details['imgsrc'] = imgs[0]['src']

  return outputDOM.prettify().encode('utf-8'), details