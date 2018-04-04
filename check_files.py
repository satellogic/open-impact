import os

from telluric.georaster import GeoRaster2, GeoRaster2IOError


def check_file(filename):
    try:
        GeoRaster2.open(filename, lazy_load=False)
    except (OSError, GeoRaster2IOError):
        logger.warning(f"Removing file {filename}")
        os.remove(filename)
    else:
        logger.info(f"File {filename} looks correct")


if __name__ == '__main__':
    import fileinput
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    for filename in fileinput.input():
        check_file(filename.strip())
