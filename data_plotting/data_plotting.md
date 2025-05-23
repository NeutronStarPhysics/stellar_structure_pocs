# Project Guide: Basic Stellar Observational Data Plotting

**Goal:** Create Python scripts to generate an HR Diagram (from Hipparcos/Gaia data) and a Mass-Luminosity relation (from binary star data).

---

### Step 1: Set Up Your Development Environment

1.  **Install Python (if you haven't already):**
    * **Recommendation:** Use **Anaconda** or **Miniconda**. These provide a robust Python distribution and make managing packages and environments much easier.
    * Download from: `conda.io/miniconda.html`

2.  **Create a Virtual Environment:**
    * **Why:** Isolates your project's dependencies from other Python projects and your system-wide Python installation, preventing conflicts.
    * **How:** Open your terminal/command prompt and use Conda:
        ```bash
        conda create -n stellar_env python=3.10  # Or a recent Python version
        conda activate stellar_env
        ```

3.  **Install Essential Python Libraries:**
    * **Why:** These are your main tools for scientific computing, data handling, and plotting.
    * **How:** With your `stellar_env` activated:
        ```bash
        pip install numpy pandas matplotlib scipy astropy astroquery
        ```
        * `numpy`: For numerical operations, especially array manipulation.
        * `pandas`: Excellent for tabular data (loading, cleaning, manipulating).
        * `matplotlib`: Your primary plotting library.
        * `scipy`: For scientific computing (useful for fitting, statistical functions later on).
        * `astropy`: Essential for astronomical units, constants, and FITS file handling.
        * `astroquery`: For programmatically querying astronomical archives (like Gaia, VizieR).

---

### Step 2: Data Acquisition Strategy

You'll need two main types of data for your plots.

1.  **For HR Diagram (Magnitude vs. Color):**
    * **Source:** Large-scale stellar surveys like **Hipparcos** (older, good historical data) or **Gaia** (current gold standard, highly precise astrometry).
    * **Key Data Points Needed:**
        * **Parallax ($\varpi$):** Crucial for calculating distance and, consequently, Absolute Magnitude. (Measured in milliarcseconds, mas).
        * **Apparent Magnitudes ($m$):**
            * **Hipparcos:** Often V-band magnitude ($V$).
            * **Gaia:** G-band, $G_{BP}$ (blue photometer), $G_{RP}$ (red photometer).
        * **Color Index:** A measure of a star's surface temperature.
            * **Hipparcos:** B-V color index (often provided).
            * **Gaia:** $G_{BP} - G_{RP}$ (computed directly from magnitudes).
        * **Error Estimates:** E.g., `parallax_error`, `G_error` (important for filtering).
        * **Quality Flags:** For Gaia, specifically look into `ruwe` (Renormalised Unit Weight Error) as a crucial filter for astrometric solution quality.

    * **How to Get Data (Option 1: `astroquery` - Recommended for Gaia):**
        * Use `astroquery.gaia` to query the Gaia archive directly. You can specify a cone search or larger queries with limits.
        * **Query Example:** Select stars with good parallax precision (e.g., `parallax_over_error > 5` or `ruwe < 1.4`). Choose magnitude ranges to keep your initial download manageable. You'll specify columns like `parallax`, `phot_g_mean_mag`, `phot_bp_mean_mag`, `phot_rp_mean_mag`, `ra`, `dec`, `source_id`, `ruwe`.
        * Download the results as an Astropy Table or Pandas DataFrame.

    * **How to Get Data (Option 2: VizieR - Good for Hipparcos and other catalogs):**
        * Use `astroquery.vizier` to access catalogs like Hipparcos (e.g., 'I/239' for Hipparcos). Specify desired columns.

2.  **For Mass-Luminosity Relation (Binary Stars):**
    * **Source:** This data is typically compiled from observations of binary star systems, which allow for direct mass measurements.
    * **Recommendation:** Search for published catalogs of fundamental stellar parameters of binary stars.
        * **Search terms:** "empirical mass luminosity relation catalog", "binary star fundamental parameters database".
        * You might find these in research papers or on dedicated astronomical data sites (VizieR may host some compiled lists).
        * **Example Catalog:** Look for "A catalogue of fundamental stellar parameters from binary systems."
    * **Key Data Points Needed:**
        * **Stellar Mass (M):** Often in solar masses ($M_\odot$).
        * **Stellar Luminosity (L):** Often in solar luminosities ($L_\odot$), or Absolute Magnitude ($M_{bol}$ or $M_V$) from which luminosity can be derived.
        * **Error bars** for mass and luminosity (if available, for advanced plotting).

    * **How to Get Data:** These are most likely available as CSV files or plain text tables downloadable from research papers or astronomy archives.

---

### Step 3: Data Loading and Initial Inspection

1.  **Load Data:**
    * **For CSV/text files:** Use `pandas.read_csv()` or `numpy.genfromtxt()`. Pandas is generally preferred due to its powerful DataFrame structure.
    * **For FITS files (common in astronomy):** Use `astropy.io.fits`. You'll read the data into an `astropy.table.Table` object, which can often be converted to a Pandas DataFrame.

2.  **Inspect Data:**
    * Use methods like `.head()`, `.info()`, and `.describe()` on your Pandas DataFrame to get a quick overview of the data's structure, column names, data types, and basic statistics.
    * Always check for missing values (NaNs).

---

### Step 4: Data Preprocessing and Calculation

This is where you'll derive the specific values needed for your plots from the raw data.

1.  **For HR Diagram (Gaia/Hipparcos Data):**
    * **Calculate Absolute Magnitude ($M_G$ for Gaia, $M_V$ for Hipparcos):**
        * **Formula:** $M = m + 5 - 5 \log_{10}(d)$, where $d$ is distance in parsecs.
        * **From Parallax:** Distance $d = 1 / (\varpi \text{ in arcseconds})$. If your parallax ($\varpi$) is in milliarcseconds (mas), the formula becomes: $d = 1000 / \varpi_{mas}$.
        * Therefore, $M = m + 5 \log_{10}(\varpi_{mas}) - 10$.
    * **Filter Data (Crucial for a clean HRD):**
        * Remove stars with **negative or zero parallax**, as these are typically unreliable measurements.
        * Filter by **`parallax_over_error`** (e.g., `> 5` or `> 10` for high precision) to ensure reliable distance calculations.
        * For Gaia, apply a **`ruwe`** filter (e.g., `< 1.4`) to exclude problematic astrometric solutions.
        * Remove rows with **NaN values** in the relevant columns (magnitudes, parallax).
        * Consider **magnitude cuts** to focus on specific stellar populations or to manage data volume.

2.  **For Mass-Luminosity Relation (Binary Data):**
    * **Ensure Consistent Units:** Verify that masses are in solar masses ($M_\odot$) and luminosities in solar luminosities ($L_\odot$). If not, convert them.
    * **Convert Absolute Magnitude to Luminosity (if necessary):**
        * The Sun's absolute bolometric magnitude is $M_{bol,\odot} \approx 4.74$.
        * The relationship is: $M_{bol} - M_{bol,\odot} = -2.5 \log_{10}(L/L_\odot)$.
        * Rearranging: $L/L_\odot = 10^{0.4 \times (M_{bol,\odot} - M_{bol})}$. You might need to apply **bolometric corrections** if your data only provides visual magnitude.
    * **Prepare for Logarithmic Plotting:** You'll likely want to plot $\log(L/L_\odot)$ vs. $\log(M/M_\odot)$. Take the logarithm of these columns.

---

### Step 5: Plotting with Matplotlib

This is where you'll use Matplotlib to visualize your processed data.

1.  **HR Diagram (Absolute Magnitude vs. Color):**
    * **Setup:**
        * `plt.figure(figsize=(width, height))`
        * Use `plt.scatter(color_index, absolute_magnitude, s=marker_size, alpha=transparency, c=color_scheme, label='Gaia Stars')`
    * **Axes Labels & Title:**
        * `plt.xlabel('G_BP - G_RP (mag)')` (for Gaia) or `'B-V (mag)'` (for Hipparcos)
        * `plt.ylabel('Absolute G Magnitude (mag)')` or `'Absolute V Magnitude (mag)'`
        * `plt.title('Hertzsprung-Russell Diagram')`
    * **Crucial for HRD:** In astronomical HR Diagrams, brighter stars (smaller absolute magnitude) are at the top. So, you must **invert the y-axis**:
        * `plt.gca().invert_yaxis()` or `plt.ylim(max_mag_value, min_mag_value)`
    * **Density Plotting (Optional, but highly recommended for large datasets):**
        * Instead of individual points, consider `plt.hexbin(color_index, absolute_magnitude, gridsize=resolution, cmap='viridis', mincnt=1)` to show star density more effectively.
    * **Adding Main Sequence/Theoretical Tracks (Advanced):** This would involve loading pre-computed model data (e.g., from MESA, PARSEC, or similar projects) and overplotting them.

2.  **Mass-Luminosity Relation (Log-Luminosity vs. Log-Mass):**
    * **Setup:**
        * `plt.figure(figsize=(width, height))`
        * `plt.scatter(log_mass, log_luminosity, s=marker_size, alpha=transparency, label='Binary Stars')`
    * **Axes Labels & Title:**
        * `plt.xlabel('Log(Mass / M_sun)')`
        * `plt.ylabel('Log(Luminosity / L_sun)')`
        * `plt.title('Stellar Mass-Luminosity Relation')`
    * **Axis Scale:** Both x and y axes should be **logarithmic** if plotting raw Mass and Luminosity, or linear if you've already taken their logs.
        * `plt.xscale('log')`
        * `plt.yscale('log')`
    * **Overplotting Theoretical Relations (Optional):**
        * For the main sequence, a simple power law $L \propto M^\alpha$ often approximates the relation ($L/L_\odot = (M/M_\odot)^\alpha$). You could plot lines with different $\alpha$ values (e.g., $\alpha \approx 3.5$ for solar-mass stars, $\alpha \approx 4$ for higher masses).

3.  **General Plot Customization:**
    * **Colors/Markers:** Choose appropriate styles for your data points.
    * **Transparency (`alpha`):** Essential for dense scatter plots to highlight data clusters.
    * **Labels and Legend:** Always label axes clearly and add a legend if plotting multiple datasets.
    * **Grid:** `plt.grid(True, linestyle=':', alpha=0.7)` for better readability.
    * **Saving:** `plt.savefig('my_hr_diagram.png', dpi=300, bbox_inches='tight')` to save your plots in high resolution.

---

### Step 6: Code Structure and Best Practices

1.  **Modular Functions:**
    * Organize your code into logical functions for reusability and clarity. Examples:
        ```python
        def load_gaia_data(query_params):
            # ...
            return df

        def calculate_absolute_magnitudes(df):
            # ...
            return df

        def filter_gaia_data(df):
            # ...
            return df

        def plot_hr_diagram(df, title):
            # ...
            plt.show() # or plt.savefig()

        # Similar functions for binary data
        def load_binary_data(filepath):
            # ...
            return df

        def plot_mass_luminosity(df, title):
            # ...
            plt.show() # or plt.savefig()
        ```

2.  **Comments & Docstrings:**
    * Explain *what* your code does and *why*.
    * Use docstrings for functions to describe their purpose, arguments, and return values.

3.  **Constants:**
    * Use `astropy.constants` for physical constants (e.g., `const.L_sun`, `const.M_sun`).
    * Define fixed values (like `parallax_over_error_cut`) at the top of your script or in a configuration section.

4.  **Main Execution Block:**
    * Structure your script with `if __name__ == "__main__":` to ensure functions are called when the script is run directly.

```python
if __name__ == "__main__":
    # Example workflow for HR Diagram
    gaia_query_params = {'radius': 5, 'ra': 0, 'dec': 0, 'limit': 10000} # Example params
    gaia_df = load_gaia_data(gaia_query_params)
    gaia_df = calculate_absolute_magnitudes(gaia_df)
    gaia_df = filter_gaia_data(gaia_df)
    plot_hr_diagram(gaia_df, "My First HR Diagram (Gaia)")

    # Example workflow for Mass-Luminosity
    binary_df = load_binary_data("path/to/your/binary_data.csv")
    plot_mass_luminosity(binary_df, "Mass-Luminosity Relation")