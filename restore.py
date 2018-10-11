import sys
import zipfile
import requests
import os

ACCESS_TOKEN = "NOAUTH" 

def get_archive_from_google(fileid):
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

if __name__ == '__main__':
  if len(sys.argv) == 3:
    # grab command line arguments
    ACCESS_TOKEN = sys.argv[1]
    ARCHIVE_ID = sys.argv[2]

    archiveHandle = open('archive.zip', 'w')
    archiveHandle.write(get_archive_from_google(ARCHIVE_ID))
    archiveHandle.close()

    if not os.path.exists('export'):
      os.makedirs('export')

    ziphandle = zipfile.ZipFile('archive.zip')
    ziphandle.extractall('export')

    os.remove('archive.zip')

    sys.stdout.write('complete')





