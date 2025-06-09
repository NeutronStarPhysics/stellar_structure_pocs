import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import astropy.units as u

from log import log_for_object


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
        # gaia_df['bp_rp_color'],
        # gaia_df['abs_g_mag'],
        gaia_df['bp_rp_color'],
        gaia_df['abs_mag'],
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

def plot_hr_diagram_lum_temp(gaia_df: pd.DataFrame, object_name: str, search_radius:  u.Quantity):

    plt.figure(figsize=(10, 8))

    # Scatter plot
    plt.scatter(
        x=gaia_df['bp_rp_color'],
        y=gaia_df['abs_mag'],
        s=3,          # Small marker size
        alpha=0.5,    # Transparency for dense regions
        color='blue'  # Or use a colormap for density
    )


    ax = plt.gca()

    # Pleiades
    ax.set_xlim([-0.2, 4.2])
    ax.set_ylim([-2, 15])

    # Omega centauri
    #ax.set_xlim([0, 2])
    #ax.set_ylim([-1, 8])

    # ax.set_xscale('log')
    # ax.set_yscale('log')

    # ax.set_ylim([ymin, ymax])

    # Invert y-axis for HR Diagram convention (brighter at top)
    ax.invert_yaxis()

    plt.xlabel('$G_{BP} - G_{RP}$ (mag)')
    plt.ylabel('Absolute G Magnitude ($M_G$)')
    plt.title(f'Gaia HR Diagram for {object_name} (Radius: {search_radius.to(u.deg):.2f} deg)')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.minorticks_on()
    plt.tight_layout()
    # plt.show()
    plt.savefig(f"../plots/{object_name.replace(' ', '_').lower()}_hr_diagram.png", dpi=300)
    log_for_object(object_name, f"HR diagram saved as hr_diagram_{object_name.replace(' ', '_').lower()}.png")
