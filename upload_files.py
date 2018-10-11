import sys
import requests
import json
import random
import string
import re
from pathlib import Path

CLIENT_ID = '209742625618-6t7ef6kfhu2e01hmi21n45b16hmqkj1m.apps.googleusercontent.com'
CLIENT_SECRET = 'tcJpmqkWBBYYH9yMxjTCrO4z'
REDIRECT_URI = 'http://encyclopedia.che.engin.umich.edu/publish.php'
ACCESS_TOKEN = "ya29.CjG8A5hjmJTsXbXy9yBiRwf0yAS7SZHUbYC5A68gDqd6v15yLc8-2azjx3wtY18n-gJO"

def enumerate_html(root):
  html = [x.resolve() for x in root.iterdir() if x.suffix == '.html']
  subdirs = [x.resolve() for x in root.iterdir() if x.is_dir()]
  for d in subdirs:
    html += enumerate_html(d)
  return html

def enumerate_dirs(root):
  subdirs = [x.resolve() for x in root.iterdir() if x.is_dir()]
  for d in subdirs:
    subdirs += enumerate_dirs(d)
  subdirs.sort()
  return subdirs

def get_dirs(root):
  return [x.resolve() for x in root.iterdir() if x.is_dir()]

def create_google_drive_directory(_dir, directories):
  url = 'https://www.googleapis.com/drive/v3/files'
  data = {
    'parents' : [directories[_dir.parent]],
    'name': _dir.name,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  headers = {'Authorization': 'Bearer '+ACCESS_TOKEN, 'Content-Type': 'application/json'}
  r = requests.post(url, json=data, headers=headers)
  if r.status_code != 200:
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "auth failed. update access token"
    exit(1)
  resp = json.loads(r.text)
  print resp
  return resp['id']

def create_google_drive_doc(html, directories):
  url = 'https://www.googleapis.com/upload/drive/v3/files'
  content_type = 'text/html'
  boundary = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
  data = {
    'parents': [directories[html.parent]],
    'name': html.name,
    'mimeType': 'application/vnd.google-apps.document'
  }
  body = '--'+boundary+'\n'
  body += 'Content-Type: application/json; charset=UTF-8\n'
  body += "\n"
  body += json.dumps(data) + "\n"
  body += "\n"
  body += '--'+boundary+'\n' 
  body += 'Content-Type: ' + content_type + '\n'
  body += "\n"
  body += open(html.as_posix(), 'rb').read() + '\n'
  body += '--'+boundary+"--"
  headers = {
    'Authorization': 'Bearer '+ACCESS_TOKEN,
    'Content-Type': 'multipart/related; boundary='+boundary,
    'Content-Length': str(len(body))
  }
  r = requests.post(url, headers=headers, data=body)
  if r.status_code != 200:
    print 'FAILURE'
    print "url:", r.request.url
    print "headers:", r.request.headers
    print "body:", r.request.body
    print "resp:", r.text
    exit(1)
  resp = json.loads(r.text)
  print resp
  return resp['id']

# oauth key retrival
if len(sys.argv) == 2:
  auth_code = sys.argv[1]
  # fs = Path('target/Pages/').resolve()
  data = {'code': auth_code, 'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'redirect_uri': REDIRECT_URI, 'grant_type': 'authorization_code'}
  r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
  creds = json.loads(r.text)
  print creds
else:
  # an API request:

  htmlsFolder = Path('Pages/').resolve()
  dirs = enumerate_dirs(htmlsFolder)

  directories = {htmlsFolder: '0B4_IzDZCQIf9Q2c3eEgtQWYzdEU'}
  googleDriveMapping = {}

  for d in dirs:
    if d not in directories:
      directories[d] = create_google_drive_directory(d, directories)

  htmls = enumerate_html(htmlsFolder)

  # pathChecker = re.compile(r'.*?(?P<path>Images.*)')
  for html in htmls:
    # m = pathChecker.match(img.as_posix())
    # url_ref = "http://encyclopedia.che.engin.umich.edu/" + m.group('path')
    create_google_drive_doc(html, directories)

  # f = open('googleDriveMapping.json', 'w')
  # f.write(json.dumps(googleDriveMapping))
  # f.close()


