#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Inspirating code from: https://github.com/CheerfulUser/TESSreduce

import logging
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
import pandas as pd


from data_retrieval import retrieve_data

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

LINE_LENGTH = 130
ROW_LIMIT = 300000

def main():    
    log.info(LINE_LENGTH*"=")
    log.info(f"HR Module")
    log.info(LINE_LENGTH*"=")

    clusters = pd.read_csv('clusters.csv').to_dict(orient='records')

    for cluster in clusters:
        log.debug(f"Cluster: {str(cluster)}")
        if cluster["Process"] == 0:
            log.info(f"Skipping {cluster['Cluster Name']}")
            log.info(LINE_LENGTH*"=")
            continue

        coord = SkyCoord(ra=cluster["Right Ascension (RA) J2000"], dec=cluster["Declination (Dec) J2000"], frame='icrs')
        retrieve_data(cluster['Cluster Name'], coord, 45 * u.arcmin, row_limit=ROW_LIMIT)
        log.info(LINE_LENGTH*"=")


if __name__ == "__main__":
    main()