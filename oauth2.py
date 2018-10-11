import requests
import sys
import json

CLIENT_ID = '209742625618-6t7ef6kfhu2e01hmi21n45b16hmqkj1m.apps.googleusercontent.com'
CLIENT_SECRET = 'tcJpmqkWBBYYH9yMxjTCrO4z'
REDIRECT_URI_PUBLISH = 'http://encyclopedia.che.engin.umich.edu/publish.php'
REDIRECT_URI_RESTORE = 'http://encyclopedia.che.engin.umich.edu/restore.php'

MEL_FOLDER_ID = "0B8mcI_zYWrPnYnpSc2tuTG9GSkE"

if len(sys.argv) == 3:
  redirect = 'NONE'
  if sys.argv[2] == 'publish':
    redirect = REDIRECT_URI_PUBLISH
  elif sys.argv[2] == 'restore':
    redirect = REDIRECT_URI_RESTORE

  data = {
    'code':           sys.argv[1], 
    'client_id':      CLIENT_ID, 
    'client_secret':  CLIENT_SECRET, 
    'redirect_uri':   redirect, 
    'grant_type':     'authorization_code'
  }
  r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
  creds = json.loads(r.text)
  if 'access_token' in creds:
    sys.stdout.write(creds['access_token'])
    exit(0)
    
  sys.stdout.write('NO_AUTH')
