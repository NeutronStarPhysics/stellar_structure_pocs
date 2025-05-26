# pip install astroquery matplotlib numpy

# #################################################################################################################################
# Using launch_job
# #################################################################################################################################

from astroquery.gaia import Gaia
import matplotlib.pyplot as plt
import numpy as np

# Define the ADQL query to retrieve Gaia data for 47 Tucanae
query = """
SELECT
    source_id, ra, dec, phot_g_mean_mag, bp_rp, parallax
FROM
    gaiadr2.gaia_source
WHERE
    CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', 6.023, -72.081, 0.5)
    ) = 1
"""

# Execute the query
job = Gaia.launch_job(query)
results = job.get_results()

# Filter out rows with missing values
filtered = results[
    (~results['parallax'].mask) &
    (~results['phot_g_mean_mag'].mask) &
    (~results['bp_rp'].mask)
]

# Calculate absolute magnitude
parallax_arcsec = filtered['parallax'] / 1000  # Convert from mas to arcsec
distance_pc = 1 / parallax_arcsec
abs_mag = filtered['phot_g_mean_mag'] - 5 * np.log10(distance_pc) + 5

# Plot the Hertzsprung-Russell diagram
plt.figure(figsize=(10, 6))
plt.scatter(filtered['bp_rp'], abs_mag, s=1, color='blue')
plt.gca().invert_yaxis()
plt.xlabel('B-V Color Index (BP - RP)')
plt.ylabel('Absolute Visual Magnitude (G)')
plt.title('Hertzsprung-Russell Diagram for 47 Tucanae')
plt.grid(True)
plt.show()


# #################################################################################################################################
# Using cone search
# #################################################################################################################################

from astroquery.gaia import Gaia
import matplotlib.pyplot as plt
import numpy as np

# Define the coordinates and radius for the cone search
ra = 6.023  # Right Ascension of 47 Tucanae
dec = -72.081  # Declination of 47 Tucanae
radius = 0.5  # Radius in degrees

# Perform the cone search
job = Gaia.cone_search_async(coord=(ra, dec), radius=radius, table="gaiadr2.gaia_source")
results = job.get_results()

# Filter out rows with missing values
filtered = results[
    (~results['parallax'].mask) &
    (~results['phot_g_mean_mag'].mask) &
    (~results['bp_rp'].mask)
]

# Calculate absolute magnitude
parallax_arcsec = filtered['parallax'] / 1000  # Convert from mas to arcsec
distance_pc = 1 / parallax_arcsec
abs_mag = filtered['phot_g_mean_mag'] - 5 * np.log10(distance_pc) + 5

# Plot the Hertzsprung-Russell diagram
plt.figure(figsize=(10, 6))
plt.scatter(filtered['bp_rp'], abs_mag, s=1, color='blue')
plt.gca().invert_yaxis()
plt.xlabel('B-V Color Index (BP - RP)')
plt.ylabel('Absolute Visual Magnitude (G)')
plt.title('Hertzsprung-Russell Diagram for 47 Tucanae')
plt.grid(True)
plt.show()

