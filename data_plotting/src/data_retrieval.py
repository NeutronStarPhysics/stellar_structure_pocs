import logging

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia

from log import log_for_object


# Columns to Retrieve and Query Filters ---
# These columns are essential for an HR Diagram and quality filtering
columns = [
    'source_id',
    'ra',
    'dec',
    'bp_rp',
    'parallax',
    'parallax_error',
    'phot_g_mean_mag',
    'phot_bp_mean_mag',
    'phot_rp_mean_mag',
    'ruwe', # Renormalised Unit Weight Error - crucial quality indicator
    'radial_velocity',
]


def retrieve_data(object_name: str, coords: SkyCoord, search_radius:  u.Quantity, row_limit: int, apply_filters: bool = True) -> pd.DataFrame:

    Gaia.ROW_LIMIT = row_limit

    # Function to retrieve data
    log_for_object(object_name, f"Searching around {object_name} (RA: {coords.ra.deg:.2f} deg, Dec: {coords.dec.deg:.2f} deg) with a radius of {search_radius}.")
    log_for_object(object_name, f"Using Gaia DR3 with a row limit of {Gaia.ROW_LIMIT}.")

    # We specify the coordinates, radius, and the ADQL query parts.
    log_for_object(object_name, "Submitting Gaia cone search query...")
    job = Gaia.cone_search_async(
        coordinate=coords,
        radius=search_radius,
        columns=columns
    )

    log_for_object(object_name, "Query submitted. Waiting for results...")
    # Blocks until job is finished and fetches the results as an Astropy Table
    table = job.get_results()
    log_for_object(object_name, f"Retrieved {len(table)} stars from Gaia DR3.")

    # Filter out rows with missing values
    filtered = table[
        (~table['parallax'].mask) &
        (~table['phot_g_mean_mag'].mask)
    ]

    # Convert to Pandas DataFrame for easier manipulation (Optional but Recommended) ---
    gaia_df = filtered.to_pandas()

    initial_rows = len(gaia_df)
    if apply_filters:
        # Apply remaining filters if not fully applied in query (or for explicit post-processing) ---
        # It's good practice to ensure all quality filters are applied explicitly.
        gaia_df.dropna(subset=['phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag', 'parallax', 'parallax_error', 'ruwe'], inplace=True)
        gaia_df = gaia_df[gaia_df['parallax_error'] < 5]
        gaia_df = gaia_df[gaia_df['ruwe'] < 1.4]

    log_for_object(object_name, f"After filtering, {len(gaia_df)} stars remain for plotting (removed {initial_rows - len(gaia_df)}).")

    # Calculate Absolute Magnitude and Color Index ---
    # For Gaia, the G_BP - G_RP color is commonly used
    gaia_df['bp_rp_color'] = gaia_df['phot_bp_mean_mag'] - gaia_df['phot_rp_mean_mag']

    # Calculate absolute magnitude
    gaia_df['abs_mag'] = gaia_df['phot_g_mean_mag'] - 5 * np.log10(1000/gaia_df['parallax']) + 5

    log_for_object(object_name, "Sample of processed data:")
    # log_for_object(object_name, gaia_df[['phot_g_mean_mag', 'bp_rp_color', 'abs_g_mag', 'parallax', 'ruwe']].head())
    log_for_object(object_name, gaia_df.head())

    return gaia_df

def bkp_retrieve_data(object_name: str, coords: SkyCoord, search_radius:  u.Quantity, row_limit: int, apply_filters: bool = True) -> pd.DataFrame:

    Gaia.ROW_LIMIT = row_limit

    # Function to retrieve data
    log_for_object(object_name, f"Searching around {object_name} (RA: {coords.ra.deg:.2f} deg, Dec: {coords.dec.deg:.2f} deg) with a radius of {search_radius}.")
    log_for_object(object_name, f"Using Gaia DR3 with a row limit of {Gaia.ROW_LIMIT}.")

    # We specify the coordinates, radius, and the ADQL query parts.
    log_for_object(object_name, "Submitting Gaia cone search query...")
    job = Gaia.cone_search_async(
        coordinate=coords,
        radius=search_radius,
        columns=columns
    )

    log_for_object(object_name, "Query submitted. Waiting for results...")
    # Blocks until job is finished and fetches the results as an Astropy Table
    table = job.get_results()
    log_for_object(object_name, f"Retrieved {len(table)} stars from Gaia DR3.")
    
    # Convert to Pandas DataFrame for easier manipulation (Optional but Recommended) ---

    gaia_df = table.to_pandas()

    initial_rows = len(gaia_df)
    if apply_filters:
        # Apply remaining filters if not fully applied in query (or for explicit post-processing) ---
        # It's good practice to ensure all quality filters are applied explicitly.
        gaia_df.dropna(subset=['phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag', 'parallax', 'parallax_error', 'ruwe'], inplace=True)
        gaia_df = gaia_df[gaia_df['parallax_error'] < 5]
        gaia_df = gaia_df[gaia_df['ruwe'] < 1.4]

    log_for_object(object_name, f"After filtering, {len(gaia_df)} stars remain for plotting (removed {initial_rows - len(gaia_df)}).")

    # Calculate Absolute Magnitude and Color Index ---
    # For Gaia, the G_BP - G_RP color is commonly used
    gaia_df['bp_rp_color'] = gaia_df['phot_bp_mean_mag'] - gaia_df['phot_rp_mean_mag']

    # Calculate absolute magnitude
    parallax_arcsec = gaia_df['parallax'] / 1000  # Convert from mas to arcsec
    distance_pc = 1 / parallax_arcsec
    abs_mag = gaia_df['phot_g_mean_mag'] - 5 * np.log10(distance_pc) + 5

    # Calculate Absolute G magnitude
    # M_G = G_mag + 5 * log10(parallax_mas) - 10
    gaia_df['abs_g_mag'] = gaia_df['phot_g_mean_mag'] + 5 * np.log10(gaia_df['parallax']) - 10

    log_for_object(object_name, "Sample of processed data:")
    # log_for_object(object_name, gaia_df[['phot_g_mean_mag', 'bp_rp_color', 'abs_g_mag', 'parallax', 'ruwe']].head())
    log_for_object(object_name, gaia_df.head())

    return gaia_df

