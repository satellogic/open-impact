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
    folder=data_dir+sceneset_id+"/"+scene_id+"/"+"attachments"+"/"
    if not os.path.exists(folder):
        os.makedirs(folder)
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
    folder=data_dir+sceneset_id+"/"+scene_id+"/"+"rasters"+"/"
    if not os.path.exists(folder):
        os.makedirs(folder)
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
def download_scene(sceneset_id,token,data_dir):
    """
    Given a set_id, and a token, download all the metadata and rasters
    files, by requesting a zipped bundle to the server, and downloading it.
    This is similar to `download_scene_set` but it downloads all the files at once using compression
    """
    import time
    url = 'https://telluric.satellogic.com/v2/scenes/download/'

    header = {'authorization': token}
    data = {'scene_id': sceneset_id,
        'async': 1}
    print("Requesting download...")
    r = requests.get(url, params=data, headers=header)
    if r.status_code != 200:
        raise ValueError("Telluric response error: %s" % r.text)
    response=requests.get(r.json()['status_path'], headers=header).json()

    #wait for server to finish
    while response['status']=='Creating':
        time.sleep(5)
        response=requests.get(r.json()['status_path'], headers=header).json()
        print("\r%s: %2.1f%% "%(response['status'],response['progress']),end="")
    print('. Ready to download.')
    url = response['download_url']
    filename = response['filename']
    header = {'authorization': token}

    r = requests.get(url, headers=header, stream=True)
    if r.status_code != 200:
        raise ValueError("Telluric response error: %s" % r.text)

    r_size=float(requests.get(url, stream=True).headers['Content-length'])
    chunk_size=128
    chunks=r_size/chunk_size
    with open(filename, 'wb') as fd:
        i=0.
        for chunk in r.iter_content(chunk_size=chunk_size):
            i+=1
            print("\r Downloading zipped file: %2.2f%%"%(i/chunks*100), end=" ")
            fd.write(chunk)
    print("Done.")

    #unzip
    import os
    from zipfile import ZipFile

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    print("Extracting...")
    with ZipFile(filename, 'r') as fp:
        fp.extractall(data_dir)
    print("Done.")
