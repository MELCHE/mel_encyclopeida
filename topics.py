import sys
import os
from bs4 import BeautifulSoup
import copy
from pathlib import Path
import re
import json
import operator

BASE_URL = "http://encyclopedia.che.engin.umich.edu"
TEMPLATE = open("menu_template.html", 'r').read()
MAIN_TEMPLATE = open("main_menu_template.html", 'r').read()
BACK_LINK_TEMPLATE = '''
  <h5>
    <a href="../menu.html">
      <i class="fa fa-caret-left fa" aria-hidden="true"></i> 
      <span class="back-link"></span>
    </a>
  </h5>
'''
ROW_TEMPLATE = '''
  <tr>
    <td class="align-middle">
      <a href="">
        <div class="col-xs-4 img">
          <img src="" class="img-fluid">
        </div>
        <div class="col-xs-8 name">
          <h4></h4>
          <p></p>
        </div>
      </a>
    <td>
  </tr>
'''
DIAGRAM_TEMPLATE = '''
  <div class="row">
    <div class="col-xs-12">
      <img src="" class="img-fluid diagram" id="">
    </div>
    <script type="text/javascript"></script>
  </div>
  
'''
SLIDE_TEMPLATE = '''
  <div class="carousel-item">
    <div class="col-sm-5">
      <img src="" class="img-fluid">
    </div>
    <div class="col-sm-7">
      <a href="">
        <h3></h3>
      </a>
      <p></p>
    </div>
  </div>
'''

def prettifyDirectoryName(directory):
  d = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', directory)
  if d.find('&') != -1:
    d = d[0:d.find('&')] + ' ' + d[d.find('&'):len(d)] # add space in front of '&'
  return d;

def indexByList(mapping, keys):
  if len(keys) == 0:
    return mapping
  if keys[0] not in mapping:
    mapping[keys[0]] = {}
  return indexByList(mapping[keys[0]], keys[1:])

def getRepresentativeImage(mapping, path):
  # print "getting rep image at path: ",  path
  pngPath = 'export/Pages/' + '/'.join(path) + '/menu.png'
  jpegPath = 'export/Pages/' + '/'.join(path) + '/menu.jpeg'
  if os.path.isfile(pngPath):
    return '/'.join(path) + '/menu.png'
  if os.path.isfile(jpegPath):
    return '/'.join(path) + '/menu.jpeg'
  if '__is_dir__' in mapping:
    for key in mapping:
      if key in ['__is_dir__', 'has_diagram', 'is_application', 'is_equipment']:
        continue
      return getRepresentativeImage(mapping[key], path + [key])

  else:
    # mapping is file
    return mapping['imgsrc']

def getSubs(mapping):
  subs = []
  if not '__is_dir__' in mapping:
    return subs
  for child in mapping:
    if child in ['__is_dir__', 'has_diagram', 'is_application', 'is_equipment']:
      continue
    subs.append(prettifyDirectoryName(child.replace('.html', '')))
  return subs

def createMenuPages(mapping, path):
  # print "creating menu page"
  # first create the menu page
  if len(path) != 0:
    menuSoup = BeautifulSoup(TEMPLATE, 'lxml')
  else:
    menuSoup = BeautifulSoup(MAIN_TEMPLATE, 'lxml')

  backlinks = menuSoup.find('div', class_='breadcrumbs').div

  table = None
  app_table = None
  eq_table = None
  if len(path) == 0:
    app_article = menuSoup.find('div', id='application-article-content')
    if app_article:
      app_table = app_article.tbody
    eq_article = menuSoup.find('div', id='equipment-article-content')
    if eq_article:
      eq_table = eq_article.tbody
  else:
    article = menuSoup.find('div', id='article-content')
    table = article.tbody


  if len(path) != 0: 
    toMenu = BeautifulSoup(BACK_LINK_TEMPLATE, 'lxml')
    toMenu.span.string = "Menu"
    toMenu.i.decompose()
    toMenu.a['href'] = (len(path) * '../') + 'menu.html'
    backlinks.append(toMenu.h5)

  # create backlinks
  for i in range(len(path)):
    backlink = BeautifulSoup(BACK_LINK_TEMPLATE, 'lxml')
    backlink.span.string = prettifyDirectoryName(path[i])
    # 1 -> 0, 2 -> 1, n -> n - 1
    backlink.a['href'] = ((len(path) - i - 1) * '../') + 'menu.html'
    backlinks.append(backlink.h5)

  # extract the child mapping
  childMapping = indexByList(mapping, path)
  if '__is_dir__' in childMapping:
    # is a directory
    childs = sorted(childMapping)

    if 'has_diagram' in childs:
      json_path = 'export/Pages/' + '/'.join(path)
      if json_path[-1] != "/":
        json_path += "/"
      json_path += 'menu.json'

      diagram_data = json.loads(open(json_path, 'r').read())
      diagram_data['id'] = "diagram_0"
      img_src = BASE_URL + '/' + diagram_data['src']
      diagram_soup = BeautifulSoup(DIAGRAM_TEMPLATE, 'lxml')


      diagram_soup.img['src'] = img_src
      diagram_soup.img['id'] = 'diagram_0'
      diagram_soup.script.string = 'var diagram_0 = ' + json.dumps(diagram_data) + ';'

      if len(path) == 0:
        app_table.insert_before(diagram_soup.div)
        eq_table.insert_before(diagram_soup.div)
      else:
        table.insert_before(diagram_soup.div)

    for child in childs:
      if child in ['__is_dir__', 'has_diagram', 'is_application', 'is_equipment']:
        continue
      # print "going over child: " + child
      childSoup = BeautifulSoup(ROW_TEMPLATE, 'lxml')
      childSoup.img['src'] = getRepresentativeImage(childMapping[child], path + [child])
      if '__is_dir__' in childMapping[child]:
        keys = [x for x in list(childMapping[child].keys()) if x not in ['__is_dir__', 'has_diagram', 'is_application', 'is_equipment']]
        # if there's only 1 child, 
        if len(keys) == 1 and '__is_dir__' not in childMapping[child][keys[0]]:
          childSoup.a['href'] = childMapping[child][keys[0]]['href']
          childSoup.h4.string = childMapping[child][keys[0]]['title']
          childSoup.p.string = childMapping[child][keys[0]]['leader']
        else:
          childSoup.a['href'] = child + "/menu.html"
          childSoup.h4.string = prettifyDirectoryName(child)
          names = childSoup.find('div', class_='name')
          subs = sorted(getSubs(childMapping[child]))
          for s in subs:
            paragraph = childSoup.new_tag('p')
            paragraph.string = s
            names.append(paragraph)

      else:
        childSoup.a['href'] = childMapping[child]['href']
        childSoup.h4.string = childMapping[child]['title']
        childSoup.p.string = childMapping[child]['leader']
      if 'is_application' in childMapping[child]:
        table = app_table
      elif 'is_equipment' in childMapping[child]:
        table = eq_table
      table.append(childSoup.tr)

    # save menuSoup to disk
    diskPath = 'export/Pages/' + '/'.join(path)
    if diskPath[-1] != "/":
      diskPath += "/"
    diskPath += 'menu.html'
    # print(diskPath)
    # print "###SAVING TO DISK###"
    f = open(diskPath, 'w')
    f.write(menuSoup.prettify().encode('utf-8'))
    f.close()

    for child in childMapping:
      if child not in ['__is_dir__', 'has_diagram', 'is_application', 'is_equipment'] and '__is_dir__' in childMapping[child]:
        createMenuPages(mapping, path + [child])

def createFeaturedCarousel(featured):
  # open up index
  indexSoup = BeautifulSoup(open('index.html', 'r').read(), 'lxml')
  indicators = indexSoup.find('ol', class_="carousel-indicators")
  inner = indexSoup.find('div', class_="carousel-inner")

  indicators.contents = []
  inner.contents = []

  for i in range(len(featured)):
    li = indexSoup.new_tag('li')
    li['data-target'] = '#featured-articles-carousel'
    li['data-slide-to'] = str(i)
    if i == 0:
      li['class'] = ['active']
    indicators.append(li)

    slide = BeautifulSoup(SLIDE_TEMPLATE, 'lxml')
    slide.img['src'] = featured[i]['imgsrc']
    slide.a['href'] = featured[i]['href']
    slide.h3.string = featured[i]['title']
    slide.p.string = featured[i]['leader']
    if i == 0:
      slide.div['class'] += ['active']

    inner.append(slide.div)

  # write to index
  f = open('index.html', 'w')
  f.write(indexSoup.prettify().encode('utf-8'))
  f.close()


def getDetails(mapping):
  if not '__is_dir__' in mapping:
    return [mapping]
  else:
    l = []
    for key in mapping:
      if key not in ['__is_dir__', 'has_diagram', 'is_application', 'is_equipment']:
        l += getDetails(mapping[key])
    return l

def loadExportMetaData():
  return json.loads(open('export_metadata.json', 'r').read())


if __name__ == '__main__':
    # grab the metadata
    metadata = loadExportMetaData()

    # extract the mapping
    mapping = metadata['files']['export']['Pages']
    path = []

    createMenuPages(mapping, path)

    # get the 10 newest pages
    details = getDetails(mapping)
    details.sort(key=operator.itemgetter('last_export_time'))
    featured = details[-10:]
    featured.reverse()

    # build index.html carousel
    createFeaturedCarousel(featured)

    sys.stdout.write('completed')
