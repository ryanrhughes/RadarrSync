import os
import logging
import requests
import json
import sys


DEV = False
VER = '1.0.1'

########################################################################################################################
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

fileHandler = logging.FileHandler("./Output.txt")
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
########################################################################################################################
logger.debug('RadarSync Version {}'.format(VER))

#Sync with normal server
radarr_url = os.environ['RADARR_URL']
radarr_key = os.environ['RADARR_KEY']
radarrSession = requests.Session()
radarrSession.trust_env = False
radarrMovies = radarrSession.get('{0}/api/movie?apikey={1}'.format(radarr_url, radarr_key))
if radarrMovies.status_code != 200:
    logger.error('Radarr server error - response {}'.format(radarrMovies.status_code))
    sys.exit(0)

#Sync with 4k server
logger.debug('syncing with 4k server')
radarr4k_url = os.environ['RADARR4K_URL']
radarr4k_key = os.environ['RADARR4K_KEY']
session = requests.Session()
session.trust_env = False
SyncServerMovies = session.get('{0}/api/movie?apikey={1}'.format(radarr4k_url, radarr4k_key))
if SyncServerMovies.status_code != 200:
    logger.error('4K Radarr server error - response {}'.format(SyncServerMovies.status_code))
    sys.exit(0)

# build a list of movied IDs already in the sync server, this is used later to prevent readding a movie that already
# exists.
# TODO refactor variable names to make it clear this builds list of existing not list of movies to add
# TODO #11 add reconcilliation to remove movies that have been deleted from source server

movieIds_to_syncserver = []
for movie_to_sync in SyncServerMovies.json():
    movieIds_to_syncserver.append(movie_to_sync['tmdbId'])
    #logger.debug('found movie to be added')

profileID = os.environ['PROFILE_ID']
newMovies = 0
searchid = []
for movie in radarrMovies.json():
    if movie['profileId'] == int(profileID):
        if movie['tmdbId'] not in movieIds_to_syncserver:
            logging.debug('title: {0}'.format(movie['title']))
            logging.debug('qualityProfileId: {0}'.format(movie['qualityProfileId']))
            logging.debug('titleSlug: {0}'.format(movie['titleSlug']))
            images = movie['images']
            for image in images:
                image['url'] = '{0}{1}'.format(radarr_url, image['url'])
                logging.debug(image['url'])
            logging.debug('tmdbId: {0}'.format(movie['tmdbId']))
            logging.debug('path: {0}'.format(movie['path']))
            logging.debug('monitored: {0}'.format(movie['monitored']))

            payload = {'title': movie['title'],
                        'qualityProfileId': movie['qualityProfileId'],
                        'titleSlug': movie['titleSlug'],
                        'tmdbId': movie['tmdbId'],
                        'path': movie['path'],
                        'monitored': movie['monitored'],
                        'images': images,
                        'profileId': movie['profileId'],
                        'minimumAvailability': movie['minimumAvailability']
                        }

            r = session.post('{0}/api/movie?apikey={1}'.format(radarr4k_url, radarr4k_key), data=json.dumps(payload))
            searchid.append(int(r.json()['id']))
            logger.info('adding {0} to server'.format(movie['title']))
        else:
            logging.debug('{0} already in library'.format(movie['title']))
    else:
        logging.debug('Skipping {0}, wanted profile: {1} found profile: {2}'.format(movie['title'], profileID, movie['profileId']))



if len(searchid):
    payload = {'name' : 'MoviesSearch', 'movieIds' : searchid}
    session.post('{0}/api/command?apikey={1}'.format(radarr4k_url, radarr4k_key), data=json.dumps(payload))

