# Inspirating code from: https://github.com/CheerfulUser/TESSreduce

Explanation and Key Considerations:

SkyCoord: Using astropy.coordinates.SkyCoord is the robust way to handle astronomical coordinates. It parses various formats and ensures accuracy.

u.arcmin (Astropy Units): It's crucial to use astropy.units for quantities like search_radius. This prevents errors from unit mismatches and makes your code more readable and reliable.
cone_search_async vs. cone_search:
cone_search_async (asynchronous): Submits the query and returns a "job" object immediately. You then call .get_results() on the job object to wait for and retrieve the data. This is better for potentially long queries as it gives you more control.
cone_search (synchronous): Blocks execution until the query is complete and returns the results directly. Simpler for quick queries.
columns parameter: Explicitly request only the columns you need. This saves bandwidth and processing time.
Quality Filters (parallax_over_error, ruwe): These are extremely important for cleaning Gaia data.
parallax_over_error: A low value indicates a poor parallax measurement. A common cut-off is > 5 or > 10.
ruwe: A measure of astrometric fit quality. For single, well-behaved stars, ruwe < 1.0 is ideal. For general samples, ruwe < 1.2 to 1.4 is often used. Higher values can indicate binarity, unresolved sources, or poor fits.
Query Limits: For very dense regions like the core of Omega Centauri, even a seemingly small radius can return millions of stars, potentially hitting Gaia archive query limits or taking a very long time.
If you encounter ADQLQueryError or timeouts, reduce your search_radius or add stricter magnitude limits (phot_g_mean_mag < X).
For very large queries, you might need to use Gaia.launch_job_async directly and write the full ADQL query string, allowing more control over the WHERE clauses and LIMIT statements.
to_pandas(): Converting the astropy.table.Table to a Pandas DataFrame is often convenient for subsequent data manipulation and analysis, as Pandas has a very rich API.
np.log10: Remember to use numpy.log10 for the logarithm calculation, as math.log10 doesn't work directly on NumPy arrays (which your DataFrame columns are).
HR Diagram Axis Inversion: Always remember to invert the y-axis (plt.gca().invert_yaxis()) for absolute magnitude plots to follow astronomical convention (brighter stars at the top).
Density Plots (hexbin): For massive datasets like Gaia, individual scatter points can overplot and hide density. plt.hexbin or 2D histograms (e.g., plt.hist2d) are excellent for visualizing star density in the HR Diagram.
This example provides a robust starting point for your HR Diagram generation from real Gaia data!



import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.gaia import Gaia

# --- 1. Define Cluster Coordinates and Search Radius ---
# You can find coordinates from SIMBAD, Wikipedia, etc.
# Omega Centauri (NGC 5139) J2000 coordinates
# RA: 13h 26m 47.2s
# Dec: -47d 28m 46s
# Let's use astropy.coordinates.SkyCoord for robust handling
omega_centauri_coords = SkyCoord(ra='13h26m47.2s', dec='-47d28m46s', frame='icrs')

# Define a search radius. Omega Cen is very large.
# A small radius (e.g., 10 arcmin) will get the core.
# A larger radius (e.g., 0.5 degrees) will get more of the halo.
# Be cautious with very large radii for dense regions, as it can hit query limits.
search_radius = 10 * u.arcmin # Let's start with 10 arcminutes (0.166 degrees)

print(f"Searching around Omega Centauri (RA: {omega_centauri_coords.ra.deg:.2f} deg, Dec: {omega_centauri_coords.dec.deg:.2f} deg) with a radius of {search_radius}.")

# --- 2. Define Columns to Retrieve and Query Filters ---
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
    'ruwe' # Renormalised Unit Weight Error - crucial quality indicator
]

# Basic ADQL (Astronomical Data Query Language) filters for quality
#   - parallax_over_error > 5: Good parallax measurement
#   - ruwe < 1.4: Good astrometric solution (recommended by Gaia for single stars)
#   - phot_g_mean_mag < 20: Limit to reasonably bright stars for initial download size
query_filters = """
    parallax_over_error > 5 AND
    ruwe < 1.4 AND
    phot_g_mean_mag IS NOT NULL AND
    phot_bp_mean_mag IS NOT NULL AND
    phot_rp_mean_mag IS NOT NULL
"""

# --- 3. Execute the Cone Search ---
# cone_search_async returns an Astropy Job object
# We specify the coordinates, radius, and the ADQL query parts.
print("\nSubmitting Gaia cone search query...")
job = Gaia.cone_search_async(
    omega_centauri_coords,
    search_radius,
    columns=columns,
    # The 'GDR2' or 'DR3' argument specifies the Gaia data release.
    # Default is usually the latest, but you can explicitly set it.
    # data_release='DR3',
    # Note: 'criteria' parameter is deprecated in newer astroquery versions.
    # Use 'constraints' or integrate into the main query string if using ADQL directly.
    # For cone_search_async, filters are often added to the SELECT clause's WHERE part.
    # Gaia.cone_search_async itself generates a basic cone query.
    # We can inject extra filters via the ADQL string when using more advanced queries,
    # or ensure they're applied after fetching. For simple cone_search, a post-filter is fine.
)

# --- 4. Get the Results ---
print("Query submitted. Waiting for results...")
# Blocks until job is finished and fetches the results as an Astropy Table
table = job.get_results()
print(f"Retrieved {len(table)} stars from Gaia DR3.")

# --- 5. Convert to Pandas DataFrame for easier manipulation (Optional but Recommended) ---
gaia_df = table.to_pandas()

# --- 6. Apply remaining filters if not fully applied in query (or for explicit post-processing) ---
# It's good practice to ensure all quality filters are applied explicitly.
initial_rows = len(gaia_df)
gaia_df.dropna(subset=['phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag', 'parallax', 'parallax_error', 'ruwe'], inplace=True)
gaia_df = gaia_df[gaia_df['parallax_over_error'] > 5]
gaia_df = gaia_df[gaia_df['ruwe'] < 1.4]
print(f"After filtering, {len(gaia_df)} stars remain for plotting (removed {initial_rows - len(gaia_df)}).")

# --- 7. Calculate Absolute Magnitude and Color Index ---
# For Gaia, the G_BP - G_RP color is commonly used
gaia_df['bp_rp_color'] = gaia_df['phot_bp_mean_mag'] - gaia_df['phot_rp_mean_mag']

# Calculate Absolute G magnitude
# M_G = G_mag + 5 * log10(parallax_mas) - 10
gaia_df['abs_g_mag'] = gaia_df['phot_g_mean_mag'] + 5 * np.log10(gaia_df['parallax']) - 10

print("\nSample of processed data:")
print(gaia_df[['phot_g_mean_mag', 'bp_rp_color', 'abs_g_mag', 'parallax', 'ruwe']].head())

# --- 8. Plot the HR Diagram ---
plt.figure(figsize=(10, 8))

# Scatter plot
plt.scatter(
    gaia_df['bp_rp_color'],
    gaia_df['abs_g_mag'],
    s=1,          # Small marker size
    alpha=0.1,    # Transparency for dense regions
    color='blue'  # Or use a colormap for density
)

# Invert y-axis for HR Diagram convention (brighter at top)
plt.gca().invert_yaxis()

plt.xlabel('$G_{BP} - G_{RP}$ (mag)')
plt.ylabel('Absolute G Magnitude ($M_G$)')
plt.title(f'Gaia HR Diagram for Omega Centauri (Radius: {search_radius.to(u.deg):.2f} deg)')
plt.grid(True, linestyle=':', alpha=0.7)
plt.minorticks_on()
plt.tight_layout()
plt.show()

# --- Optional: Plotting density instead of individual points for very dense clusters ---
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
plt.title(f'Gaia HR Diagram Density for Omega Centauri (Radius: {search_radius.to(u.deg):.2f} deg)')
plt.grid(True, linestyle=':', alpha=0.7)
plt.minorticks_on()
plt.tight_layout()
plt.show()