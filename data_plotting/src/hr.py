#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Inspirating code from: https://github.com/CheerfulUser/TESSreduce

import logging
import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
import pandas as pd

import data_retrieval as dr

# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

LINE_LENGTH = 130
# ROW_LIMIT = 300000
ROW_LIMIT = 1000
RUN_ALL = False
PLOT_SINGLE = True  # Set to True to plot a single cluster, False to plot all clusters

def main():    
    log.info(LINE_LENGTH*"=")
    log.info(f"HR Module")
    log.info(LINE_LENGTH*"=")

    clusters = pd.read_csv('clusters.csv').to_dict(orient='records')
    search_radius = 45 * u.arcmin  # Search radius for Gaia query

    data_frames = []

    for cluster in clusters:
        log.debug(f"Cluster: {str(cluster)}")
        if cluster["Process"] == 0 and RUN_ALL == False:
            log.debug(f"Skipping {cluster['Cluster Name']}")
            log.debug(LINE_LENGTH*"=")
            continue
        cluster_name = cluster["Cluster Name"].strip()
        coord = SkyCoord(ra=cluster["Right Ascension (RA) J2000"], dec=cluster["Declination (Dec) J2000"], frame='icrs')

        data_frame = dr.retrieve_data(cluster_name, coord,search_radius, row_limit=ROW_LIMIT, apply_filters=False)
        data_frames.append(data_frame)
        if PLOT_SINGLE:
            dr.plot_hr_diagram (data_frame, cluster_name, search_radius)
            # dr.plot_density_diagram (data_frame, cluster_name, search_radius)

        log.info(LINE_LENGTH*"=")
    if not PLOT_SINGLE:
        rows = len(data_frames) / 2
        dr.plot_frames(data_frames, figsize=(rows, 2))


if __name__ == "__main__":
    main()