#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Inspirating code from: https://github.com/CheerfulUser/TESSreduce

import logging
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia

from data_retrieval import retrieve_data

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
log = logging.getLogger(__name__)

def main():    
    log.info(80*"=")
    log.info(f"HR Module")
    log.info(80*"=")

    clusters = [
        {
            'name': 'Omega Centauri',
            'coords': SkyCoord(ra='13h26m47.2s', dec='-47d28m46s', frame='icrs'),
            'search_radius': 30 * u.arcmin,
            'row_limit': 300000
        },
        {
            'name': '47 Tucanae',
            'coords': SkyCoord(ra='00h24m05.5s', dec='-72d04m53.2s', frame='icrs'),
            'search_radius': 45 * u.arcmin,
            'row_limit': 300000
        }
    ]
    for cluster in clusters:
        retrieve_data(cluster['name'], cluster['coords'], cluster['search_radius'], row_limit=cluster['row_limit'])

if __name__ == "__main__":
    main()