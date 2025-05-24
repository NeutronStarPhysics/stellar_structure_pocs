import logging

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.gaia import Gaia

log = logging.getLogger(__name__)

# Columns to Retrieve and Query Filters ---
# These columns are essential for an HR Diagram and quality filtering
columns = [
    'source_id',
    'ra',
    'dec',
    'parallax',
    'parallax_error',
    'phot_g_mean_mag',
    'phot_bp_mean_mag',
    'phot_rp_mean_mag',
    'ruwe', # Renormalised Unit Weight Error - crucial quality indicator
    'radial_velocity'
]

def log_for_object(object_name: str, message: str):
    """
    Log a message for a specific object.
    """
    log.info(f"[{object_name}] {message}")


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

    # Calculate Absolute G magnitude
    # M_G = G_mag + 5 * log10(parallax_mas) - 10
    gaia_df['abs_g_mag'] = gaia_df['phot_g_mean_mag'] + 5 * np.log10(gaia_df['parallax']) - 10

    log_for_object(object_name, "Sample of processed data:")
    # log_for_object(object_name, gaia_df[['phot_g_mean_mag', 'bp_rp_color', 'abs_g_mag', 'parallax', 'ruwe']].head())
    log_for_object(object_name, gaia_df.head())

    return gaia_df

def plot_frames(dataframes, figsize=(15, 5)):

    n = len(dataframes)
    fig, axes = plt.subplots(1, n, figsize=figsize, sharey=True)
    if n == 1:
        axes = [axes]
    for i, (df, ax) in enumerate(zip(dataframes, axes)):

        # Scatter plot
        plt.scatter(
            df['bp_rp_color'],
            df['abs_g_mag'],
            s=3,          # Small marker size
            alpha=0.5,    # Transparency for dense regions
            color='blue'  # Or use a colormap for density
        )

        # Invert y-axis for HR Diagram convention (brighter at top)
        plt.gca().invert_yaxis()


        ax.minorticks_on()
        ax.invert_yaxis()
    
    plt.tight_layout()
    plt.savefig(f"../plots/all_hr_diagrams.png", dpi=300)



def plot_density_diagram(gaia_df: pd.DataFrame, object_name: str, search_radius:  u.Quantity):
    # --- Plotting density instead of individual points for very dense clusters ---
    # You can use hexbin or kde for density mapping
    plt.figure(figsize=(10, 8))
    plt.hexbin(
        gaia_df['bp_rp_color'],
        gaia_df['abs_g_mag'],
        gridsize=100, # Number of bins in the x-direction
        cmap='viridis',
        mincnt=1      # Minimum number of points in a bin to be displayed
    )
    plt.gca().invert_yaxis()
    plt.colorbar(label='Number of stars')
    plt.xlabel('$G_{BP} - G_{RP}$ (mag)')
    plt.ylabel('Absolute G Magnitude ($M_G$)')
    plt.title(f'Gaia HR Diagram Density for {object_name} (Radius: {search_radius.to(u.deg):.2f} deg)')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.minorticks_on()
    plt.tight_layout()
    plt.show()
    plt.savefig(f"../plots/{object_name.replace(' ', '_').lower()}_hr_diagram_density.png", dpi=300)
    log_for_object(object_name, f"HR diagram density saved as hr_diagram_density_{object_name.replace(' ', '_').lower()}.png")

def plot_hr_diagram(gaia_df: pd.DataFrame, object_name: str, search_radius:  u.Quantity):

    plt.figure(figsize=(10, 8))

    # Scatter plot
    plt.scatter(
        gaia_df['bp_rp_color'],
        gaia_df['abs_g_mag'],
        s=3,          # Small marker size
        alpha=0.5,    # Transparency for dense regions
        color='blue'  # Or use a colormap for density
    )

    # Invert y-axis for HR Diagram convention (brighter at top)
    plt.gca().invert_yaxis()

    plt.xlabel('$G_{BP} - G_{RP}$ (mag)')
    plt.ylabel('Absolute G Magnitude ($M_G$)')
    plt.title(f'Gaia HR Diagram for {object_name} (Radius: {search_radius.to(u.deg):.2f} deg)')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.minorticks_on()
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"../plots/{object_name.replace(' ', '_').lower()}_hr_diagram.png", dpi=300)
    log_for_object(object_name, f"HR diagram saved as hr_diagram_{object_name.replace(' ', '_').lower()}.png")
