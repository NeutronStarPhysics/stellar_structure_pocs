#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Inspirating code from: https://github.com/CheerfulUser/TESSreduce

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia
import pandas as pd
import data_plots as dp

import data_retrieval as dr
from log import log_for_object

import logging
import yaml


# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)


CONFIG_FILE = "config.yaml"

def read_config():
    cfg = {}
    with open(CONFIG_FILE) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    return cfg

def main():    
    cfg = read_config()
    clusters = pd.read_csv(cfg["INPUT_FILE"]).to_dict(orient='records')

    log.info(cfg["LINE_LENGTH"]*"=")
    log.info(f"HR Module")
    log.info(f"Input File: {cfg['INPUT_FILE']}")
    log.info(cfg["LINE_LENGTH"]*"=")

    search_radius = 60 * u.arcmin  # Search radius for Gaia query

    data_frames = []

    for cluster in clusters:
        log.debug(f"Cluster: {str(cluster)}")
        if cluster["Process"] == 0 and cfg["RUN_ALL"] == False:
            log.debug(f"Skipping {cluster['Cluster Name']}")
            log.debug(cfg["LINE_LENGTH"]*"=")
            continue
        cluster_name = cluster["Cluster Name"].strip()
        log.info(f"Processing cluster: {cluster_name}")        
        log.info(cfg["LINE_LENGTH"]*"=")

        coord = SkyCoord(ra=cluster["Right Ascension (RA) J2000"], dec=cluster["Declination (Dec) J2000"], frame='icrs')

        data_frame = dr.retrieve_data(cluster_name, coord, search_radius, row_limit=cfg["ROW_LIMIT"], apply_filters=True)
        data_frames.append(data_frame)
        if cfg["PLOT_SINGLE"]:
            # dp.plot_hr_diagram (data_frame, cluster_name, search_radius)
            # dr.plot_density_diagram (data_frame, cluster_name, search_radius)
            dp.plot_hr_diagram_lum_temp(data_frame, cluster_name, search_radius)

        log.info(cfg["LINE_LENGTH"]*"=")
    if not cfg["PLOT_SINGLE"]:
        rows = len(data_frames) / 2
        dp.plot_frames(data_frames, figsize=(rows, 2))


if __name__ == "__main__":
    main()