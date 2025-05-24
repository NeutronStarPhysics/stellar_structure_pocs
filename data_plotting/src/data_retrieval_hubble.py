from astropy.coordinates import SkyCoord
from astropy import units as u
from astroquery.mast import Observations # This is the primary module for querying MAST

# --- 1. Define Target Coordinates ---
# J2000 coordinates for Mayall II (G1)
mayall_ii_coords = SkyCoord(ra='00h32m46.51s', dec='+39d34m39.7s', frame='icrs')

# --- 2. Define Search Radius ---
# Mayall II is a dense cluster. A small radius is usually sufficient for cluster members.
# For a cluster in another galaxy, a few arcseconds is appropriate as individual stars
# would only be resolved in the very core by HST. If you want to see the whole cluster
# as an extended object, you might need a slightly larger radius, but be careful with
# general field-of-view sizes of HST instruments.
search_radius = 5.0 * u.arcsec # Let's start with 5 arcseconds. You can adjust this.

print(f"Querying MAST for HST data around Mayall II (G1):")
print(f"  RA: {mayall_ii_coords.ra.deg:.4f} deg, Dec: {mayall_ii_coords.dec.deg:.4f} deg")
print(f"  Radius: {search_radius}")

# --- 3. Construct and Execute the Query ---
# We'll use Observations.query_criteria to search the MAST archive.
# obs_collection='HST' specifies that we only want Hubble Space Telescope data.
# s_ra, s_dec, s_radius define the cone search.
print("\nSubmitting query to MAST...")
obs_table = Observations.query_criteria(
    obs_collection='HST',
    s_ra=mayall_ii_coords.ra.deg,
    s_dec=mayall_ii_coords.dec.deg,
    s_radius=search_radius.to(u.deg).value # s_radius expects degrees
)

print(f"Found {len(obs_table)} observations.")

# --- 4. Inspect the Results ---
# The result is an Astropy Table. You can inspect its columns.
print("\nColumns in the results table:")
print(obs_table.colnames)

# Print a few lines of the table to see the types of data
print("\nSample of results:")
print(obs_table[['obsid', 'instrument_name', 'target_name', 'filters', 't_exptime', 'calib_level', 'productFilename']].head())

# Filter by instrument if you're looking for specific data (e.g., WFC3 or ACS)
# HST has various instruments over its lifetime (e.g., ACS, WFC3, WFPC2, STIS, COS)
acs_obs = obs_table[obs_table['instrument_name'] == 'ACS/WFC']
wfc3_obs = obs_table[obs_table['instrument_name'] == 'WFC3/UVIS'] # Or WFC3/IR
print(f"\nFound {len(acs_obs)} ACS observations and {len(wfc3_obs)} WFC3 observations.")

# Filter by Calibration Level:
# Level 2 (CALIB) is usually the calibrated, ready-to-use science data.
# Level 3 (HLSP) are higher-level science products (e.g., mosaics, catalogs).
# Level 0 (RAW) is raw uncalibrated data.
calibrated_data = obs_table[obs_table['calib_level'] == 2]
print(f"Found {len(calibrated_data)} calibrated (Level 2) observations.")

# --- 5. Download Data Products (Optional) ---
# To download the actual FITS files, you typically select the desired products
# from the observation table and then use download_products().
# IMPORTANT: Downloading large amounts of HST data can take time and consume disk space.
# Also, most HST data has a 1-year proprietary period from its observation date.
# You will only be able to download public data unless you are the PI of the observation.

# Let's try to get a list of products (e.g., calibrated images)
# 'productGroupDescription' can be 'SCIENCE', 'CALIBRATION', 'PREVIEW', etc.
# 'productType' can be 'SCIENCE', 'PREVIEW', 'METADATA', etc.
# For images, 'productFilename' often ends in '_drz.fits' (drizzled) or '_flt.fits' (flat-fielded)
print("\nIdentifying products for download...")
# Select up to 5 science products to download for demonstration purposes
# This is a highly selective filter to avoid downloading too much
products_to_download = Observations.get_product_list(calibrated_data)
# Filter for actual science image files (e.g., drizzled images from ACS/WFC)
science_images = products_to_download[
    (products_to_download['productGroupDescription'] == 'SCIENCE') &
    (products_to_download['productFilename'].str.contains('drz.fits', na=False))
]

print(f"Found {len(science_images)} science image products.")

if len(science_images) > 0:
    print(f"Downloading up to {min(5, len(science_images))} science image products...")
    # Downloads to './mastDownload/HST/<obsid>/' subdirectories
    Observations.download_products(science_images[:min(5, len(science_images))],
                                   mpr=False) # mpr=False prevents downloading metadata products
    print("Download complete (check the 'mastDownload' directory).")
else:
    print("No relevant science image products found to download for this query.")

# --- Further Steps (After Downloading FITS Files) ---
# 1. Read FITS files: Use astropy.io.fits to open the downloaded files.
#    from astropy.io import fits
#    with fits.open('path/to/your/file.fits') as hdul:
#        data = hdul[0].data # Or hdul[1].data depending on FITS structure
#        header = hdul[0].header
#
# 2. Display Images: Use matplotlib.pyplot.imshow to display the image data.
#    You might need to adjust colormaps, stretches (e.g., log scale) for astronomical images.
#
# 3. WCS (World Coordinate System): Use astropy.wcs to convert pixel coordinates to sky coordinates
#    and vice-versa, allowing you to plot stars on the image if you have a separate catalog.