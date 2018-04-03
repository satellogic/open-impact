"""Downloads ALL the data.

1. Get all the available scene ids for a user
2. Download all the rasters of a given scene
3. Parallelize the whole thing

"""
import os
import logging

from concurrent.futures import ThreadPoolExecutor

import requests


TELLURIC_ERROR_MSG = "telluric response error: %s"

AUTH_URL = 'https://auth.telluric.satellogic.com/api-token-auth/'
LIST_SCENES_URL = 'https://telluric.satellogic.com/v2/scenes/'


def auth(user, password):
    """Returns the authentication token.

    Parameters
    ----------
    user : str
        Username.
    password : str
        Password.

    Returns
    -------
    session : requests.Session
        Authenticated requests Session.

    Examples
    --------
    ...

    """
    data = {
        'username': user,
        'password': password,
    }
    req = requests.post(AUTH_URL, data=data)
    if req.status_code != 200:
        raise ValueError(TELLURIC_ERROR_MSG % req.text)

    token = "JWT " + req.json()['token']

    session = requests.Session()
    session.headers = {'authorization': token}

    return session


def get_all_scenes(session, product_name=None):
    """Gets all available rasters.

    Parameters
    ----------
    session : requests.Session
        An open requests Session.
    product_name : str
        Product name to filter (optional, default to None).

    Yields
    ------
    Scene IDs.

    """
    # TODO: Do proper pagination
    params = {'limit': 4000}
    if product_name:
        params.update({'productname': product_name})

    req = session.get(LIST_SCENES_URL, params=params)
    if req.status_code != 200:
        raise ValueError(TELLURIC_ERROR_MSG % req.text)

    for raster in req.json()['results']:
        yield raster['scene_id']


def download_raster(session, url, filename):
    """Downloads a particular raster to disk.

    If by any reason the download is interrupted or fails, the file
    is removed to avoid incomplete rasters.

    Parameters
    ----------
    session : requests.Session
        An open requests Session.
    url : str
        Raster URL to download.
    filename : str
        Filename to use on disk.

    """
    req = session.get(url, stream=True)
    content_length = int(req.headers['content-length'])

    try:
        with open(filename, 'wb') as fd:
            for chunk in req.iter_content(chunk_size=128):
                fd.write(chunk)
    finally:
        if os.path.getsize(filename) < content_length:
            logging.warning(f"Removing unfinished download {filename}")
            os.remove(filename)


def get_all_rasters(session, scene_id):
    """Downloads all rasters from a given scene ID.

    Parameters
    ----------
    session : requests.Session
        An open requests Session.
    scene_id : str
        Scene ID.

    Yields
    ------
    Pairs (filename, url).

    """
    params = {'scene_id': scene_id}

    req = session.get(LIST_SCENES_URL, params=params)
    if req.status_code != 200:
        raise ValueError(TELLURIC_ERROR_MSG % req.text)

    for raster in req.json()['results'][0]['rasters']:
        yield raster['url'], raster['file_name']


def main(user, password, dry_run=False, product_name='cube'):
    with ThreadPoolExecutor(max_workers=5) as executor:
        with auth(user, password) as s:
            for scene_id in get_all_scenes(s, product_name):
                logger.info(f"Rasters corresponding to scene_id {scene_id}:")
                if not os.path.exists(scene_id):
                    os.makedirs(scene_id)

                for url, filename in get_all_rasters(s, scene_id):
                    path = os.path.join(scene_id, filename)
                    if os.path.exists(path):
                        logger.info(f"Skipping existing raster {path}")
                    else:
                        logger.info(f"Downloading raster {path}...")
                        if not dry_run:
                            try:
                                executor.submit(download_raster, s, url, path)
                            except Exception as exc:
                                logger.error(f"Error: {str(exc)}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    user = os.environ["TELLURIC_USERNAME"]
    password = os.environ["TELLURIC_PASSWORD"]

    main(user, password)
