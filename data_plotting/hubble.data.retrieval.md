# Project Guide: Querying Hubble Space Telescope (HST) for Mayall II (G1) Data

You've chosen a fascinating and exceptionally important object to query with HST! Mayall II (also known as G1) is a truly remarkable globular cluster, notable because it belongs to the **Andromeda Galaxy (M31)**, not our own Milky Way.

This means that while Gaia data is excellent for stars within the Milky Way, it won't resolve individual stars in Mayall II. To study individual stars in Mayall II, astronomers rely on powerful telescopes like Hubble.

Here's a detailed breakdown of the steps involved in querying the HST archive for Mayall II data using Python, primarily leveraging `astroquery.mast`.

---

### Step 1: Define Your Target Coordinates and Search Radius

First, you need to pinpoint Mayall II in the sky and determine how large of an area you want to search around it.

* **Target Coordinates:** Use the J2000 coordinates for Mayall II (G1):
    * **Right Ascension (RA):** 00h 32m 46.51s
    * **Declination (Dec):** +39° 34′ 39.7″
    * You'll use `astropy.coordinates.SkyCoord` to handle these robustly.

* **Search Radius:** Since Mayall II is a dense globular cluster in another galaxy, individual stars are only resolvable by HST in the very core. A small radius is typically sufficient. Starting with a few **arcseconds** (e.g., 5-10 arcseconds) is a good approach. You can adjust this based on the field of view of specific HST instruments or if you're looking for the cluster as an extended object rather than resolving individual stars.

---

### Step 2: Construct and Execute the Query

You'll use `astroquery.mast.Observations` to interact with the Mikulski Archive for Space Telescopes (MAST).

* **Specify Observation Collection:** Crucially, you'll set `obs_collection='HST'` to filter results specifically for Hubble Space Telescope data.
* **Cone Search Parameters:** Provide the Right Ascension (`s_ra`), Declination (`s_dec`), and search radius (`s_radius`) to `Observations.query_criteria()`. Remember that `s_radius` typically expects the radius in degrees.
* **Executing the Query:** The `query_criteria()` call itself performs the search and returns an `Astropy Table` object containing metadata for all matching observations.

---

### Step 3: Inspect the Results

Once you receive the `Astropy Table` of observations, you'll want to inspect its contents to understand what data is available.

* **Column Names:** Check `obs_table.colnames` to see all available metadata fields (e.g., `obsid`, `instrument_name`, `target_name`, `filters`, `t_exptime`, `calib_level`, `productFilename`).
* **Sample Data:** Print a few rows using `obs_table.head()` to get a quick overview of the data types and values.
* **Filtering by Instrument:** HST has had various instruments over its lifetime (e.g., ACS, WFC3, WFPC2, STIS, COS). You can filter the table by `instrument_name` if you're looking for data from a specific camera.
* **Calibration Level:** Look at the `calib_level` column:
    * `calib_level=2` typically indicates calibrated, science-ready data.
    * `calib_level=0` is raw, uncalibrated data.
    * `calib_level=3` often represents Higher-Level Science Products (HLSPs), such as mosaics or specialized catalogs derived from multiple observations.

---

### Step 4: Download Data Products (Optional but Highly Relevant)

After identifying interesting observations, you can download the actual data files (usually FITS files).

* **Identifying Products:** Use `Observations.get_product_list()` on your filtered observation table. This will generate a list of all associated data products for those observations.
* **Filtering Products:** Filter this product list further by `productGroupDescription` (e.g., 'SCIENCE', 'PREVIEW') and `productType` (e.g., 'IMAGE', 'SPECTRUM'). For HST images, you'll often look for filenames ending in `_drz.fits` (drizzled, combined images) or `_flt.fits` (flat-fielded, single exposure images).
* **Downloading:** Use `Observations.download_products()` on your filtered product list. You can limit the number of files to download to manage disk space. By default, downloads go to a `mastDownload/HST/` subdirectory.

---

### Important Considerations for HST Data:

* **Data Volume:** HST data files (FITS files) can be quite large. Be mindful of your disk space and internet bandwidth, especially for large queries.
* **Proprietary Period:** Most newly acquired HST data has a 1-year proprietary period. During this time, only the original proposal's Principal Investigator (PI) and their team can access it. After one year, the data becomes public. Your queries will only retrieve public data unless you have specific PI access.
* **MAST Account:** While you can query and download public data without an account, creating a free MAST account and configuring `astroquery` with your credentials can sometimes offer benefits like improved download speeds or managing larger download queues.
* **Further Analysis:** Downloaded FITS files are not immediately ready for plotting like a simple table. They are astronomical images or spectra. Analyzing them typically requires further processing steps using libraries like `astropy.io.fits` to open the files, `matplotlib.pyplot.imshow` to display images, and potentially `astropy.wcs` for world coordinate system transformations to align images with sky coordinates.

---

This framework will guide you through acquiring HST data for Mayall II. Happy exploring!