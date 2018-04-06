# Accessing data

Across all projects, one of the common needs is to access the satellite data. This document explains how to find imagery data, and download it.


## Satellogic Data

There are 2 ways to get Satellogic data:

* Via the web interfacte on [Telluric/catalog](http://telluric.satellogic.com/catalog).
* Via the Telluric API interfacte on [Telluric](https://telluric.satellogic.com/docs/).
    * On the API you can request of a zipped file for download (might take a few minutes), or you can get each raster directly without delay.

### Via web interface

You should have received a user/password (if not, email brunosan@satellogic.com). This is an example [of the search in the Catalog for Gambia](https://telluric.satellogic.com/catalog/shared/N4IgRghgzgpgthADiAXCAFgF04qKD0+A1gPYBOJAdhAHQDmMJdNArpQJYC06M7AJjAA2YGGWYD8mdoJhR8FCHyh18ADwC8wVQF8AZAE9N+vQC9NJ7SAA0IAMYxKmUagDanAIwBOAOyeADN4ArDSeAEzeAMx+EQAsAGyeEVbugYF+Mak0oRERoWmBEQAccQC6NrYsZGQOmADK9pQwAJIAIqggjQDuUBCYEQD6CLYU-RUi-XneMIV+gaG2cXyeMWDeoYoQfquFhe6Rvu4AZhD9fv0x-RHWdoLstkQwfPUOzW1oXT19gxDDJKMs40m01m80Wy1W6z4m22u32niOJzOFyuNnQJAAbqJHs9Gq1UJQWIJBDYEOxKAAFCCNQQAYUq1UcABUIGB2tUoITMFBrodpE4yAAlEgsJzclAuFwgQ4kEg4MhkzAgMqSjmIRC3ZzKkCICh8Fi2TDUOAwJVWSVSY1QTAQODILVQBowfr8U0qx2wTDOviukCfIS3Jz9I0mkplEAARxYon0qFA0tlOoV7WAAB0QJh9IgYGmUGnySRBPo6FQ01Y07YZWQ+GTerIcxK3O5CjQInEZnEm7t0pEAskYjQYn44oPPIF3LMYqFPMVlR5m63253xzEe95kqEB1FQnFQn5EnFW4FZ+4N-5Zv5QqFB35CstQuvN35t7v94fj6e-Oen1fP7fJ32ByHEcxwnKcZzNOcWzbIcl27KI13cftB2HPcQMCSdp1KUNLBsP0iXYQNg3aa4HReL1iNw90YE9F00BIlg1Q1MgKKlCg4H6C0TTomxMD+TiWNuOACNQcdPxsEhDkOD1UD8ElqI2a1Y20GwdRIPUDSItAxhNZSQBMGU4FQOIaG8GJChyCzLIsmw+DICBOlEWprUwFgxRAEgs0ab0eI8nFXnaD5egGIYRm0iZAimGY5gWJYVjWDYtm8HY9giA5jlOc5Lmuch2DoGtBD8vF3hgbogu+X5-kBCLgWisE4shaEkthVL4XSpEstw8gpEoOgADF2CEJRXFACgRS4lwwykTAZCc+UepYw5CUESlMHQFiHhjbj3KrZw6OUkbhScVxJoImbMDmugFqWla1q2jaWPIARmL2qwDrG46eNOmBZrJS6tsWokbvWmBNpAbKduesHtBKbQgA).


### Via API

First we need to authenticate:

```python
#Authenticate on telluric
import requests
url = 'https://auth.telluric.satellogic.com/api-token-auth/'
payload = {'username':'stanfordhackathon','password':'******'}

print("Getting token...")
r = requests.post(url, data=payload)
if r.status_code != 200:
    raise ValueError("Telluric response error: %s" %r.text) 
telluric_token="JWT "+r.json()['token']
print(telluric_token[0:10]+"*masked*")
```

Then we can, for example, search for scences intersecting a point:

```python
#get scene id
import json

# https://telluric.satellogic.com/docs/#operation/list
url = 'https://telluric.satellogic.com/v2/scenes/'

footprint ={
        "type": "Point",
        "coordinates": [
          -16.64703369140625,
          13.447059093856021
        ]
      }

payload = {'footprint': json.dumps(footprint),
           'productname':'cube'}
header = { 'authorization' : telluric_token}
print("Requesting scene...")
r = requests.get(url, params=payload, headers=header)
if r.status_code != 200:
    raise ValueError("Telluric response error: %s" %r.text) 
response=r.json()
scene_id=response['results'][0]['scene_id']
print(scene_id)
```

Once the `scene_id` is identified, we can download a single raster:

```python
#download specific hyperspectral band to a file (<30 s with a good connection)
raster_827 = response['results'][0]['rasters'][1]

url = raster_827['url']
filename = raster_827['file_name']
header = { 'authorization' : telluric_token}

# http://docs.python-requests.org/en/master/user/quickstart/#raw-response-content
r = requests.get(url, headers=header, stream=True)
if r.status_code != 200:
    raise ValueError("Telluric response error: %s" %r.text) 

with open(filename, 'wb') as fd:
    for chunk in r.iter_content(chunk_size=128):
        fd.write(chunk)
```



## Landsat Data

Download data from https://earthexplorer.usgs.gov/

Search from: 2017-11-01 to 2018-02-22

Coordinates: Select ROI with the following instructions

![](gambia_image_coordinates2.png)

## Hyperion data
