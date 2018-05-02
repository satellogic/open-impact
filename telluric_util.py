"""
Set of higher level utility functions for common operations
To use inside the examples of this repository use:

import sys
sys.path.insert(0, '../')
import telluric_util
telluric_util.get_token
"""


import requests

def get_token( user, passwd ):
  """
  Given a `user` and `passwd` strings, returns the auth token for Telluric.
  In case of error it Raises an error
  """

  url = 'https://auth.telluric.satellogic.com/api-token-auth/'
  payload = {'username': user, 'password': passwd}
  r = requests.post(url, data=payload)
  if r.status_code != 200:
    raise ValueError("%s: Telluric response error: %s" % (r.status_code,r.text))

  telluric_token = "JWT "+r.json()['token']
  return telluric_token

def set2id(set_id,token):
  """
  Given a set_id, and a token, return the scence_id.
  A set_id refers to the Level 0 data, scence_id has been processed into Level 1
  using the latest code (last number on the scene_id string).
  """
  header = {'authorization': token}
  url = 'https://telluric.satellogic.com/v2/scenes'
  payload = {'sceneset_id':set_id}
  r = requests.get(url, params=payload,headers=header)
  if r.status_code != 200:
        raise ValueError("Telluric response error: %s" % r.text)
  response = r.json()
  scene_id=response['results'][0]['scene_id']
  return scene_id

def download_scene_iter(sceneset_id,token,data_dir):
      """
      Given a set_id, and a token, download all the metadata and rasters
      files, file by file.
      This is similar to `download_scene` but it checks each file individually
      """
    import time
    import os

    url = 'https://telluric.satellogic.com/v2/scenes/'
    header = {'authorization': token}
    payload = {'sceneset_id': sceneset_id}
    r = requests.get(url, headers=header, params=payload)
    if r.status_code != 200:
        raise ValueError("Telluric response error: %s" % r.text)
    r=r.json()
    if r["count"] != 1:
        raise ValueError("Telluric search returned %i scenesets, expected 1."%r["count"])

    scene_id=r['results'][0]["scene_id"]
    folder=data_dir+sceneset_id+"/"+scene_id+"/"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    print("Checking for %i metadata files:"%(len(r['results'][0]['attachments'])))
    for file in r['results'][0]['attachments']:
        print(file['file_name'])
        url = file['url']
        filename = folder+file['file_name']
        if not os.path.exists(filename):
            r = requests.get(url)
            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
    print("Checking for %i rasters files:"%(len(r['results'][0]['rasters'])))
    for file in r['results'][0]['rasters']:
        print(file['file_name'])
        url = file['url']
        filename = folder+file['file_name']
        if not os.path.exists(filename):
            r = requests.get(url)
            with open(filename, 'wb') as fd:
                for chunk in r.iter_content(chunk_size=128):
                    fd.write(chunk)
