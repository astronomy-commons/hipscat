"""Generate a molleview map with the pixel densities of the catalog

NB: Testing validity of generated plots is currently not tested in our unit test suite.
"""

from typing import Any, Dict, List, Union

import healpy as hp
import matplotlib.colors as mcolors
import numpy as np
from matplotlib import pyplot as plt

from hipscat.catalog import Catalog
from hipscat.io import file_io, paths
from hipscat.pixel_math import HealpixPixel


def _read_point_map(catalog_base_dir, storage_options: Union[Dict[Any, Any], None] = None):
    """Read the object spatial distribution information from a healpix FITS file.

    Args:
        catalog_base_dir: path to a catalog
    Returns:
        one-dimensional numpy array of long integers where the value at each index
        corresponds to the number of objects found at the healpix pixel.
    """
    map_file_pointer = paths.get_point_map_file_pointer(catalog_base_dir)
    return file_io.read_fits_image(map_file_pointer, storage_options=storage_options)


def plot_points(catalog: Catalog, projection="moll", **kwargs):
    """Create a visual map of the input points of an in-memory catalog.

    Args:
        catalog (`hipscat.catalog.Catalog`) Catalog to display
        projection (str) The map projection to use. Valid values include:
            - moll - Molleweide projection (default)
            - gnom - Gnomonic projection
            - cart - Cartesian projection
            - orth - Orthographic projection
    """
    if not catalog.on_disk:
        raise ValueError("on disk catalog required for point-wise visualization")
    point_map = _read_point_map(catalog.catalog_base_dir, storage_options=catalog.storage_options)
    _plot_healpix_map(point_map, projection, f"Catalog point density map - {catalog.catalog_name}", **kwargs)


def plot_pixels(catalog: Catalog, projection="moll", **kwargs):
    """Create a visual map of the pixel density of the catalog.

    Args:
        catalog (`hipscat.catalog.Catalog`) Catalog to display
        projection (str) The map projection to use. Valid values include:
            - moll - Molleweide projection (default)
            - gnom - Gnomonic projection
            - cart - Cartesian projection
            - orth - Orthographic projection
    """
    pixels = catalog.get_healpix_pixels()
    plot_pixel_list(
        pixels=pixels,
        plot_title=f"Catalog pixel density map - {catalog.catalog_name}",
        projection=projection,
        **kwargs,
    )


def plot_pixel_list(pixels: List[HealpixPixel], plot_title: str = "", projection="moll", **kwargs):
    """Create a visual map of the pixel density of a list of pixels.

    Args:
        pixels: healpix pixels (order and pixel number) to visualize
        plot_title (str): heading for the plot
        projection (str) The map projection to use. Valid values include:
            - moll - Molleweide projection (default)
            - gnom - Gnomonic projection
            - cart - Cartesian projection
            - orth - Orthographic projection
    """
    max_order = np.max(pixels).order
    min_order = np.min(pixels).order

    if max_order == min_order:
        color = plt.cm.viridis(0.5)  # pylint: disable=no-member
        colors = [plt.cm.viridis(0.0), color]  # pylint: disable=no-member
        cmap = mcolors.LinearSegmentedColormap.from_list("my_colormap", colors)
    else:
        num_colors = max_order - min_order + 1
        colors = plt.cm.viridis(np.linspace(0, 1, num_colors))  # pylint: disable=no-member
        cmap = mcolors.LinearSegmentedColormap.from_list("my_colormap", colors, num_colors)

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
    _plot_healpix_map(order_map, projection, plot_title, cmap=cmap, **kwargs)


def _plot_healpix_map(healpix_map, projection, title, cmap="viridis", **kwargs):
    """Perform the plotting of a healpix pixel map.

    Args:
        healpix_map: array containing the map
        projection: projection type to display
        title: title used in image plot
        cmap: matplotlib colormap to use
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

    projection_method(healpix_map, title=title, nest=True, cmap=cmap, **kwargs)
    plt.plot()
