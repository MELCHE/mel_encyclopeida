import sys
import requests
import json
import random
import string
import re
from datetime import datetime
from pathlib import Path
import shutil
import os
import zipfile

CLIENT_ID = '209742625618-6t7ef6kfhu2e01hmi21n45b16hmqkj1m.apps.googleusercontent.com'
CLIENT_SECRET = 'tcJpmqkWBBYYH9yMxjTCrO4z'
REDIRECT_URI = 'http://encyclopedia.che.engin.umich.edu/publish.php'
ACCESS_TOKEN = "NO_AUTH"

BACKUPS_FOLDER = "0B4_IzDZCQIf9cVF6VUsza21qU3c"

def upload_zip_file(zipfile, name):
  url = 'https://www.googleapis.com/upload/drive/v3/files'
  content_type = 'application/zip'
  boundary = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
  data = {
    'parents': [BACKUPS_FOLDER],
    'name': zipfile.name,
  }
  body = '--'+boundary+'\n'
  body += 'Content-Type: application/json; charset=UTF-8\n'
  body += "\n"
  body += json.dumps(data) + "\n"
  body += "\n"
  body += '--'+boundary+'\n' 
  body += 'Content-Type: ' + content_type + '\n'
  body += "\n"
  body += open(zipfile.as_posix(), 'rb').read() + '\n'
  body += '--'+boundary+"--"
  headers = {
    'Authorization': 'Bearer ' + ACCESS_TOKEN,
    'Content-Type': 'multipart/related; boundary='+boundary,
    'Content-Length': str(len(body))
  }
  r = requests.post(url, headers=headers, data=body)
  if r.status_code != 200:
    sys.stderr.write('FAILURE\n') 
    sys.stderr.write("url:" + r.request.url + '\n')
    sys.stderr.write("headers:" + r.request.headers + '\n')
    sys.stderr.write("body:" + r.request.body + '\n')
    sys.stderr.write("resp:" + r.text + '\n')
    exit(1)

def zipup(name, path):
  zipf = zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED)
  for root, dirs, files in os.walk(path):
    for file in files:
      zipf.write(os.path.join(root, file))
  zipf.close()

if len(sys.argv) == 2:
  ACCESS_TOKEN = sys.argv[1]
  headers = {"Authorization": "Bearer " + ACCESS_TOKEN}

  # get the name info
  r = requests.get('https://www.googleapis.com/drive/v3/about?fields=user', headers=headers)
  profile = json.loads(r.text)
  email = profile['user']['emailAddress']
  uniquename = email[:email.find('@')]

  zipfilename = uniquename +"_"+ datetime.now().isoformat().replace(':', '.')

  # create the destination directory if it doesn't already exist
  if not os.path.exists('tmp'):
    os.makedirs('tmp')

  zipup('tmp/'+zipfilename+'.zip', 'Pages')
  zipfilepath = Path('tmp/'+zipfilename+'.zip').resolve()

  upload_zip_file(zipfilepath, zipfilename+".zip")

  # delete out our tmp folder since we're done 
  shutil.rmtree('tmp')

  sys.stdout.write(zipfilename+'.zip') # success execution signal


