"""Generate a molleview map with the pixel densities of the catalog

NB: Testing validity of generated plots is currently not tested in our unit test suite.
"""

import healpy as hp
import numpy as np
from matplotlib import pyplot as plt

from hipscat.catalog import Catalog
from hipscat.io import file_io, paths


def _read_point_map(catalog_base_dir):
    """Read the object spatial distribution information from a healpix FITS file.

    Args:
        catalog_base_dir: path to a catalog
    Returns:
        one-dimensional numpy array of long integers where the value at each index
        corresponds to the number of objects found at the healpix pixel.
    """
    map_file_pointer = paths.get_point_map_file_pointer(catalog_base_dir)
    return file_io.read_fits_image(map_file_pointer)


def plot_points(catalog: Catalog, projection="moll", draw_map=True):
    """Create a visual map of the input points of the catalog.

    Args:
        catalog (`hipscat.catalog.Catalog`) Catalog to display
        projection (str) The map projection to use. Valid values include:
            - moll - Molleweide projection (default)
            - gnom - Gnomonic projection
            - cart - Cartesian projection
            - orth - Orthographic projection
    """
    point_map = _read_point_map(catalog.catalog_base_dir)
    _plot_healpix_map(
        point_map,
        projection,
        f"Catalog point density map - {catalog.catalog_name}",
        draw_map=draw_map,
    )


def plot_pixels(catalog: Catalog, projection="moll", draw_map=True):
    """Create a visual map of the pixel density of the catalog.

    Args:
        catalog (`hipscat.catalog.Catalog`) Catalog to display
        projection (str) The map projection to use. Valid values include:
            - moll - Molleweide projection (default)
            - gnom - Gnomonic projection
            - cart - Cartesian projection
            - orth - Orthographic projection
    """
    pixels = catalog.partition_info.get_healpix_pixels()
    max_order = catalog.partition_info.get_highest_order()

    order_map = np.full(hp.order2npix(max_order), hp.pixelfunc.UNSEEN)

    for pixel in pixels:
        explosion_factor = 4 ** (max_order - pixel.order)
        exploded_pixels = [
            *range(
                pixel.pixel * explosion_factor,
                (pixel.pixel + 1) * explosion_factor,
            )
        ]
        order_map[exploded_pixels] = pixel.order
    _plot_healpix_map(
        order_map,
        projection,
        f"Catalog pixel density map - {catalog.catalog_name}",
        draw_map=draw_map,
    )


def _plot_healpix_map(healpix_map, projection, title, draw_map=True):
    """Perform the plotting of a healpix pixel map.

    Args:
        healpix_map: array containing the map
        projection: projection type to display
        title: title used in image plot
    """
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

    if draw_map:  # pragma: no cover
        projection_method(
            healpix_map,
            title=title,
            nest=True,
        )
        plt.plot()
