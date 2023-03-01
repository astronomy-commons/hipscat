"""Generate a molleview map with the pixel densities of the catalog"""

import healpy as hp
import numpy as np
from matplotlib import pyplot as plt

from hipscat.catalog import Catalog


def plot_pixels(catalog: Catalog, projection="moll"):
    """Create a visual map of the pixel density of the catalog.

    Args:
        catalog (`hipscat.catalog.Catalog`) Catalog to display
        projection (str) The map projection to use. Valid values include:
            - moll - Molleweide projection (default)
            - gnom - Gnomonic projection
            - cart - Cartesian projection
            - orth - Orthographic projection

    """
    pixels = catalog.get_pixels()

    catalog_orders = pixels.order.unique()
    catalog_orders.sort()
    max_order = catalog_orders[-1]

    order_map = np.full(hp.order2npix(max_order), hp.pixelfunc.UNSEEN)

    for _, pixel in pixels.iterrows():
        explosion_factor = 4 ** (max_order - pixel.order)
        exploded_pixels = [
            *range(pixel.pixel * explosion_factor, (pixel.pixel + 1) * explosion_factor)
        ]
        order_map[exploded_pixels] = pixel.order

    if projection == "moll":
        projection_method = hp.mollview
    elif projection == "gnom":
        projection_method = hp.gnomview
    elif projection == "cart":
        projection_method = hp.cartview
    elif projection == "orth":
        projection_method = hp.orthview
    else:
        raise NotImplementedError(f"unknown projection: {projection}")

    projection_method(
        order_map,
        max=max_order,
        title=f"Catalog density map - {catalog.catalog_name}",
        nest=True,
    )
    # return plt.plot()
