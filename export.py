import sys
import os
import requests
import json
import random
import string
import re
from pathlib import Path
import urllib
import googleDriveCleaner
import shutil
import rfc3339
import datetime

ACCESS_TOKEN = "NO_AUTH"

ROOT_PAGES_DIRECTORY_ID = '0B4_IzDZCQIf9Q2c3eEgtQWYzdEU'
FILES_EXPORTED = 0
ARTICLE_TEMPLATE = open('article_template.html', 'r').read()

BASE_URL = "http://encyclopedia.che.engin.umich.edu/"

NOW = datetime.datetime.now(rfc3339.UTC_TZ).isoformat()
FORCE_PUBLISH = "NEW"

# debug = " "

def prettifyDirectoryName(directory):
  return re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', directory)

def indexByList(mapping, keys):
  if len(keys) == 0:
    return mapping
  if keys[0] not in mapping:
    mapping[keys[0]] = {}
  return indexByList(mapping[keys[0]], keys[1:])


def list_childs(parentFolderId, metadata):
  # global debug
  url = "https://www.googleapis.com/drive/v3/files?"
  LAST_EXPORT_TIME = rfc3339.parse_datetime(metadata['last_export_time'])
  if FORCE_PUBLISH == 'FORCE':
    # force it to get everything at least 10 years old
    LAST_EXPORT_TIME = LAST_EXPORT_TIME - datetime.timedelta(weeks=52*10)
  parameters = {
    'q':"('"+parentFolderId+"' in parents and mimeType = 'application/vnd.google-apps.folder') or ('"+parentFolderId+"' in parents and modifiedTime > '"+LAST_EXPORT_TIME.isoformat()+"')",
    'fields': 'files(id,mimeType,name)'
  }
  headers = {'Authorization': 'Bearer '+ACCESS_TOKEN}
  r = requests.get(url+urllib.urlencode(parameters), headers=headers)
  if r.status_code != 200:
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "response:",  r.text
    print "auth failed. update access token"
    exit(1)
  else:
    results = json.loads(r.text)
    # process the files returned
    if results['files'] != None:
      # debug += r.text + ' '
      return results['files']
    else:
      return []

def filter_folders(resources):
  folders = []
  for r in resources:
    if r['mimeType'] == 'application/vnd.google-apps.folder' and not r['name'].upper().startswith('(WIP'):
      folders.append(r)
  return folders

def filter_files(resources):
  files = []
  for r in resources:
    if r['mimeType'] == 'application/vnd.google-apps.document' and not r['name'].upper().startswith('(WIP'):
      r['name'] = r['name'].split('.')[0]+'.html'
      files.append(r)
  return files

def filter_images(resources):
  images = []
  for r in resources:
    if r['mimeType'] == 'image/jpeg' and not r['name'].upper().startswith('(WIP'):
      r['name'] = 'menu.jpeg'
      images.append(r)
    elif r['mimeType'] == 'image/png' and not r['name'].upper().startswith('(WIP'):
      r['name'] = 'menu.png'
      images.append(r)
  return images

def filter_jsons(resources):
  jsons = []
  for r in resources:
    if r['mimeType'] == 'application/json':
      if r['name'] != 'application.json' and r['name'] != 'equipment.json':
        r['name'] = 'menu.json'
      jsons.append(r)
  return jsons

def get_file_from_google(fileid):
  global FILES_EXPORTED
  url = "https://www.googleapis.com/drive/v3/files/"+fileid+"/export?mimeType=text%2Fhtml"
  headers = {'Authorization': 'Bearer '+ACCESS_TOKEN}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "response:",  r.text
    print "auth failed. update access token"
    exit(1)
  else:
    FILES_EXPORTED += 1
    # sys.stderr.write("export size: "+str(len(r.text)) + "\n")
    return r.text.encode('utf-8')

def get_img_from_google(fileid):
  url = "https://www.googleapis.com/drive/v3/files/"+fileid+"?alt=media"
  headers = {'Authorization': 'Bearer '+ACCESS_TOKEN}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "response:",  r.text
    print "auth failed. update access token"
    exit(1)
  else:
    # fetch the webContentLink
    return r.content

def get_json_from_google(fileid):
  url = "https://www.googleapis.com/drive/v3/files/"+fileid+"?alt=media"
  headers = {'Authorization': 'Bearer '+ACCESS_TOKEN}
  r = requests.get(url, headers=headers)
  if r.status_code != 200:
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "response:",  r.text
    print "auth failed. update access token"
    exit(1)
  else:
    # fetch the webContentLink
    return r.text.encode('utf-8')

def create_folder_with(dst):
  if not os.path.exists(dst):
    os.makedirs(dst)

def create_file_with(name, contents):
  # print "writing file " + name 
  global ARTICLE_TEMPLATE
  f = open(name, 'w')
  # sys.stderr.write("exporting: "+name + "\n")
  article_html, details = googleDriveCleaner.googleDriveCleaner(contents, ARTICLE_TEMPLATE)
  f.write(article_html)
  f.close()
  details['href'] = BASE_URL + name.replace('export/', '')
  title = prettifyDirectoryName(Path(name).stem)
  details['title'] = title
  return details

def create_img_with(name, contents):
  # print "writing img " + name
  f = open(name, 'wb')
  # sys.stderr.write("exporting: "+name + "\n")
  f.write(contents)
  f.close()

def create_json_with(name, contents):
  f = open(name, 'w')
  f.write(contents)
  f.close()

def export_to_fs(directory, metadata):
  # get children of this directory
  path = '/'.join(directory['path']) + '/'
  # print "processing: " + path
  childResources = list_childs(directory['id'], metadata)
  folderResources = filter_folders(childResources)
  fileResources = filter_files(childResources)
  imageResources = filter_images(childResources)
  jsonResources = filter_jsons(childResources)

  dir_mapping = indexByList(metadata['files'], directory['path'])
  dir_mapping['__is_dir__'] = True

  # for every imageResource, fetch the data and create a img
  for i in imageResources:
    img = get_img_from_google(i['id'])
    create_img_with(path + i['name'], img)

  # for every fileResource, fetch the data and create a file
  for f in fileResources:
    html = get_file_from_google(f['id'])
    details = create_file_with(path + f['name'], html)
    details['last_export_time'] = NOW
    details['just_updated'] = True
    dir_mapping[f['name']] = details
    # print "created file: ", directory['path'] + f['name']

  # for every jsonReource, fetch the data and save it to disk
  for j in jsonResources:
    if j['name'] == 'application.json':
      dir_mapping['is_application'] = True
    elif j['name'] == 'equipment.json':
      dir_mapping['is_equipment'] = True
    else:
      jsontext = get_json_from_google(j['id'])
      create_json_with(path + j['name'], jsontext)
      dir_mapping['has_diagram'] = True

  # for every folderResource, create a folder and recurse on the directory
  for f in folderResources:
    next_dir = {'path': directory['path'] + [f['name']], 'id': f['id']}
    next_path = path + f['name'] + '/'
    create_folder_with(next_path)
    export_to_fs(next_dir, metadata)

def loadExportMetaData():
  return json.loads(open('export_metadata.json', 'r').read())

def storeExportMetaData(data):
  f = open('export_metadata.json', 'w')
  f.write(json.dumps(data))
  f.close()

def ignoreDuringCopy(directory, contents):
    return ["menu.html", "menu.png", "menu.jpeg"]

if __name__ == '__main__':
  if len(sys.argv) == 3:
    ACCESS_TOKEN = sys.argv[1]
    FORCE_PUBLISH = sys.argv[2]

    dst = ['export', 'Pages']

    dstPath = '/'.join(dst)
    # if a previous path exists, delete it
    if os.path.exists(dstPath):
      shutil.rmtree(dstPath)

    metadata = loadExportMetaData()

    if FORCE_PUBLISH == 'NEW':
      # copy over Pages/*, creating the directory in the process.
      shutil.copytree("Pages/", dstPath, ignore=ignoreDuringCopy)
    elif FORCE_PUBLISH == 'FORCE':
      os.makedirs(dstPath)
      metadata = {"files": {}, "last_export_time": "2018-04-05T17:40:46.599424+00:00"}

    export_to_fs({'id': ROOT_PAGES_DIRECTORY_ID, 'path': dst}, metadata)
    sys.stdout.write(str(FILES_EXPORTED))

    metadata['last_export_time'] = NOW
    storeExportMetaData(metadata)
# print get_file_from_google('16yCLoEjnwIZkYlk8CT_0IAiL20VB-rvqGd7a2-UnMHQ')


# childResources = list_childs(ROOT_PAGES_DIRECTORY_ID)
# folders = filter_folders(childResources)
# for f in folders:
#   print f['name']
# print "Number of subfolders:", len(filter_folders(childResources))
# print "Number of files:", len(filter_files(childResources))
