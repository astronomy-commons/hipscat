from hipscat.catalog import Catalog
from hipscat.inspection import plot_pixels, plot_points


def test_generate_map_order1(small_sky_dir_cloud, example_cloud_storage_options):
    """Basic test that map data can be generated (does not test that a plot is rendered)"""
    cat = Catalog.read_from_hipscat(small_sky_dir_cloud, storage_options=example_cloud_storage_options)
    plot_pixels(cat, draw_map=False)
    plot_points(cat, draw_map=False)
