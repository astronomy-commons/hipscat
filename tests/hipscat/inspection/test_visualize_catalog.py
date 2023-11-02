import pytest

from hipscat.catalog import Catalog
from hipscat.inspection import plot_pixel_list, plot_pixels, plot_points


@pytest.mark.parametrize("projection", ["moll", "gnom", "cart", "orth"])
def test_generate_map(small_sky_dir, projection):
    """Basic test that map data can be generated (does not test that a plot is rendered)"""

    cat = Catalog.read_from_hipscat(small_sky_dir)
    plot_pixels(cat, projection=projection, draw_map=False)
    plot_points(cat, projection=projection, draw_map=False)


def test_generate_map_unknown_projection(small_sky_dir):
    """Test for error with unknown projection type"""

    cat = Catalog.read_from_hipscat(small_sky_dir)
    with pytest.raises(NotImplementedError):
        plot_pixels(cat, projection=None, draw_map=False)

    with pytest.raises(NotImplementedError):
        plot_pixels(cat, projection="", draw_map=False)

    with pytest.raises(NotImplementedError):
        plot_pixels(cat, projection="projection", draw_map=False)


def test_generate_map_order1(small_sky_order1_dir):
    """Basic test that map data can be generated (does not test that a plot is rendered)"""

    cat = Catalog.read_from_hipscat(small_sky_order1_dir)
    plot_pixels(cat, draw_map=False)
    plot_points(cat, draw_map=False)


def test_visualize_in_memory_catalogs(catalog_info, catalog_pixels):
    """Test behavior of visualization methods for non-on-disk catalogs and pixel data."""
    catalog = Catalog(catalog_info, catalog_pixels)
    plot_pixels(catalog, draw_map=False)
    plot_pixel_list(catalog_pixels, plot_title="My special catalog", draw_map=False)

    with pytest.raises(ValueError, match="on disk catalog required"):
        plot_points(catalog, draw_map=False)
