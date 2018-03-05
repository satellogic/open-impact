# Local Routing server

This document explain who to run a local server to give, much faster, travel times, in custom types of vehicles, on a custom region.

The alternative is to use e.g. [Mapbox API](https://www.mapbox.com/api-documentation/#matrix) or [OSRM API](http://project-osrm.org/docs/v5.10.0/api/#general-options).

For this tutorial, we focus on a region (the Gambia), and a mode of transportation (a truck).

## Overview

0. Install software
1. Download [or update] OSM data
2. Download and run routing engine OSRM.
3. Sample routing called

## 0. Install Software.

You'll need:
* osmconvert:
 `wget -O - http://m.m.i24.cc/osmconvert.c | cc -x c - -lz -O3 -o osmconvert`
* osmupdate
`wget -O - http://m.m.i24.cc/osmupdate.c | cc -x c - -o osmupdate`
* [Gdal](http://www.gdal.org/)
* [docker](https://docs.docker.com/install/)

## 1. Download and sync OSM data


Establish a Bounding box around The Gambia. Add a generous buffer around it, since sometimes to go to you destination you might take a better road around the region.

[![](gambia-roi.png)](https://gist.github.com/brunosan/b10932ecba1b792dc4ade0f4fb41c81b)

```sh
    wget https://gist.githubusercontent.com/brunosan/b10932ecba1b792dc4ade0f4fb41c81b/raw/7b4f530c186e79071225a8f862ffb65974d38e88/map.geojson
   ogrinfo map.geojson map | grep Extent
   BBOX="-17.995605,11.243062,-12.963867,15.135764"

   #Download the latest OSM data:
   DATE=`date '+%Y-%m-%d'`
   mkdir data/
   cd data/
   wget -P data/ -O gambia_$DATE.osm "http://overpass.osm.rambler.ru/cgi/xapi_meta?*[bbox=$BBOX]"
   #]*
```

* OPTIONAL, Convert to 05m file format (MUCH smaller)
```sh
../osmconvert -v gambia_$DATE.osm -o=gambia_$DATE.o5m
```

* OPTIONAL, If you want to merge updates from OSM
```sh
../osmupdate -v gambia_$DATE.o5m gambia_$DATE_tmp.o5m -b=$BBOX
```

## 2. Download and run routing engine OSRM.

First, if you don't want to use default driving properties (e.g. a car), you should also define the ones of the vehicle you will be using for the travel times (top speed, types of roads it can travel, ...). I created a quick `truck.lua` based on the standard `car.lua` and lowering the top speed.

Follow instructions on [OSRM](https://github.com/Project-OSRM/osrm-backend), these are basically 3 lines of code:

```sh
docker run -t -v $(pwd):/data osrm/osrm-backend osrm-extract -p /data/truck.lua /data/gambia_2018-02-20.osm

docker run -t -v $(pwd):/data osrm/osrm-backend osrm-partition /data/gambia_2018-02-20.osrm

docker run -t -v $(pwd):/data osrm/osrm-backend osrm-customize /data/gambia_2018-02-20.osrm

#run the server locally
docker run -t -i -p 5000:5000 -v $(pwd):/data osrm/osrm-backend osrm-routed --algorithm mld /data/gambia_2018-02-20.osrm
```

OPTIONAL, run a front-end to check the results, on http://127.0.0.1:9966
```sh
docker run -p 9966:9966 osrm/osrm-frontend
```

[![](frontend.png)](http://localhost:9966/?z=8&center=14.048666%2C-15.188599&loc=14.721761%2C-17.418823&loc=13.480448%2C-13.958130&hl=en&alt=0)


## 3. Sample routing called

### Simple OD pair

To get the time and distance from a origin-destination point:

For example, the travel time, and distance from origin `[14.721761,-17.418823]` to the destination `[13.480448,-13.958130]`:

```python
import requests  #http framework to make Mapbox API requests for routes
import json # handle response as json
import datetime # save timestamp

url="http://localhost:5000/route/v1/driving/"
comma="%2C"
sep="%3B"
origin=[14.721761,-17.418823]
destination=[13.480448,-13.958130]
fullurl=url+str(origin[1])+','+str(origin[0])+";"+str(destination[1])+','+str(destination[0])
response = requests.get(fullurl) #do the request
response.raise_for_status() # ensure we notice bad responses
print, fullurl
# http://localhost:5000/route/v1/driving/-17.418823,14.721761;-13.95813,13.480448'
print, json.loads(response.text)['routes'][0]['distance']," meters"
# 510247, ' meters'
print, json.loads(response.text)['routes'][0]['duration']," seconds"
# 0281.4, ' seconds'
```

### Matrix of OsDs

Most likely you will have a set of origins and a set of destinations, and you want to calculate the travel times from each origin to each destination. OSRM offers a `matrix` function for this case.

For this example we will use [OSM Taginfo](https://taginfo.openstreetmap.org/) to find a set of origins and a set of destinations, and then download them from [Overpass turbo](https://overpass-turbo.eu/).

Concretely we will use [all Gambian villages](https://overpass-turbo.eu/s/wJo) as sources, and all [Gambian health facilities](https://data.humdata.org/dataset/gambia-healthsites) as destinations.

See [Matrix ETA.ipynb](./Matrix ETA.ipynb).
