import requests
import sys
import json

MEL_FOLDER_ID = "0B8mcI_zYWrPnYnpSc2tuTG9GSkE"

if __name__ == '__main__':
  if len(sys.argv) == 2:
    accessToken = sys.argv[1]

    headers = {"Authorization": "Bearer " + accessToken}
    r = requests.get("https://www.googleapis.com/drive/v3/about?fields=user", headers=headers)
    about = json.loads(r.text)
    permissionId = about['user']['permissionId']

    # check that they have permissions on the MEL folder
    r = requests.get("https://www.googleapis.com/drive/v3/files/"+MEL_FOLDER_ID+"/permissions", headers=headers)
    permissions_list = json.loads(r.text)

    for permission in permissions_list['permissions']:
      if permission['id'] == permissionId and permission['role'] in ['writer', 'reader']:
        sys.stdout.write(accessToken)
        exit(0)

