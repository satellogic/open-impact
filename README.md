# Open Impact

This repository compiles several social and/or environmental impact projects.

Where available, we leverage open software (like python) and open data (like Landsat), as well as Satellogic open data (under the reproducible academic research program, see [license.md](license.md))


Each idea has an explanation at the top, how to read the data, and a few pointers of the tools you might need. This is not an exclusive list, if there's a similar idea wit the same data, feel free to work on it. These are just pointers to ignite your curiosity and get you up and running as quickly as possible.


## City fingerprint.

Can we create a measure that compares cities how the look from space? Could it be used to detect similar cities? Could it detect changes of population, if it's a green city, a brick and asphalt city, ...

Data:
- Geojson list of 200 cities around the world with metadata like population at several times.
- Landsat/Copernicus Level-1 at different times.
- Satellogic Hyperspectral where available.
- Historical Hyperion where available.

Concept:

- Cluster the hyperspectral data from many cities into K-means or other algorithms. Force historical data of the same city to be in the same cluster (emphasize permanent information) or in different clusters (emphasize sensitivity to changes in population or other factors).

- Use Open Street Map data to calculate the % content for each satellite pixel (e.g. A landsat pixel might cover 10% park, 20% road, ...). This can be used to predict OSM in unkown places, the pixels with most error might indicate new constructions or features.

[Notebook](#)


## Forest fire recovery

Can we predict recovery times from a forest fire? What makes for a fastest recovery?

Data:
- Landsat/Copernicus Level-1 at different times.
- Satellogic Hyperspectral where available.
- Historical Hyperion where available.

Concept:

Take data from right before a fire to after it's fully recovered. Use the hyperspectral and temporal information to adjust to a recovery interpolation. Once done, it should be possible to map quick recoveries and what makes them so.

[Notebook](#)


## Access to market

One of the most important aspects in development is access to resources, from hospitals, to schools to markets. The idea of this project is to create the accessibility curve for a region highly dependent on this accessibility.

Data:
- Landsat/Copernicus Level-1 at different times.
- Satellogic Hyperspectral where available.
- Historical Hyperion where available.

[Notebook](#)

3- Gambia field 2 market access. Hacer land classification y luego assignarlo a la ciudad mas cercana, calcular la curva de recursos naturales y si distancia por carretera a los centros de las ciudades. Esto usa OSM para el routing. (edited)


## Ocean color

TBD

[Notebook](#)
