import requests
import sys
import urllib

BACKUPS_FOLDER_ID = "0B4_IzDZCQIf9cVF6VUsza21qU3c"
ACCESS_TOKEN = "NO_AUTH"

def list_archives():
  url = "https://www.googleapis.com/drive/v3/files?"
  parameters = {
    'q': "'"+BACKUPS_FOLDER_ID+"' in parents",
    'fields': 'files(id,name,createdTime)',
    'orderBy': 'createdTime desc'
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
    sys.stdout.write(r.text)

if __name__ == '__main__':
  if len(sys.argv) == 2:
    ACCESS_TOKEN = sys.argv[1]
    list_archives()
