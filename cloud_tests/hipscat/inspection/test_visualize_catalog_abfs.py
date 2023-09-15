import pytest
import os

from hipscat.catalog import Catalog
from hipscat.inspection import plot_pixels, plot_points


@pytest.mark.parametrize("projection", ["moll", "gnom", "cart", "orth"])
def test_generate_map(example_abfs_path, example_abfs_storage_options, projection):
    """Basic test that map data can be generated (does not test that a plot is rendered)"""
    small_sky_dir = os.path.join(example_abfs_path, "data", "small_sky")
    cat = Catalog.read_from_hipscat(small_sky_dir, storage_options=example_abfs_storage_options)
    plot_pixels(cat, projection=projection, draw_map=False)
    plot_points(cat, projection=projection, draw_map=False)


def test_generate_map_unknown_projection(example_abfs_path, example_abfs_storage_options):
    """Test for error with unknown projection type"""

    small_sky_dir = os.path.join(example_abfs_path, "data", "small_sky")
    cat = Catalog.read_from_hipscat(small_sky_dir, storage_options=example_abfs_storage_options)

    with pytest.raises(NotImplementedError):
        plot_pixels(cat, projection=None, draw_map=False)

    with pytest.raises(NotImplementedError):
        plot_pixels(cat, projection="", draw_map=False)

    with pytest.raises(NotImplementedError):
        plot_pixels(cat, projection="projection", draw_map=False)


def test_generate_map_order1(example_abfs_path, example_abfs_storage_options):
    """Basic test that map data can be generated (does not test that a plot is rendered)"""
    small_sky_order1_dir = os.path.join(example_abfs_path, "data", "small_sky_order1")
    cat = Catalog.read_from_hipscat(small_sky_order1_dir, storage_options=example_abfs_storage_options)
    plot_pixels(cat, draw_map=False)
    plot_points(cat, draw_map=False)
