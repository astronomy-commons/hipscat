"""Tests of catalog functionality"""

import os

import healpy as hp
import numpy as np
import pytest

from hipscat.catalog import Catalog, CatalogType, PartitionInfo
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_math.validators import ValidatorsErrors
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def test_catalog_load(catalog_info, catalog_pixels):
    catalog = Catalog(catalog_info, catalog_pixels)
    assert catalog.get_healpix_pixels() == catalog_pixels
    assert catalog.catalog_name == catalog_info.catalog_name

    for hp_pixel in catalog_pixels:
        assert hp_pixel in catalog.pixel_tree
        assert catalog.pixel_tree[hp_pixel].node_type == PixelNodeType.LEAF


def test_catalog_load_wrong_catalog_info(base_catalog_info, catalog_pixels):
    with pytest.raises(TypeError):
        Catalog(base_catalog_info, catalog_pixels)


def test_catalog_wrong_catalog_type(catalog_info, catalog_pixels):
    catalog_info.catalog_type = CatalogType.INDEX
    with pytest.raises(ValueError):
        Catalog(catalog_info, catalog_pixels)


def test_partition_info_pixel_input_types(catalog_info, catalog_pixels):
    partition_info = PartitionInfo.from_healpix(catalog_pixels)
    catalog = Catalog(catalog_info, partition_info)
    assert len(catalog.get_healpix_pixels()) == len(catalog_pixels)
    assert len(catalog.pixel_tree.root_pixel.get_all_leaf_descendants()) == len(catalog_pixels)
    for hp_pixel in catalog_pixels:
        assert hp_pixel in catalog.pixel_tree
        assert catalog.pixel_tree[hp_pixel].node_type == PixelNodeType.LEAF


def test_tree_pixel_input(catalog_info, catalog_pixels):
    tree = PixelTreeBuilder.from_healpix(catalog_pixels)
    catalog = Catalog(catalog_info, tree)
    assert len(catalog.get_healpix_pixels()) == len(catalog_pixels)
    assert len(catalog.pixel_tree.root_pixel.get_all_leaf_descendants()) == len(catalog_pixels)
    for pixel in catalog_pixels:
        assert pixel in catalog.pixel_tree
        assert catalog.pixel_tree[pixel].node_type == PixelNodeType.LEAF


def test_tree_pixel_input_list(catalog_info, catalog_pixels):
    catalog = Catalog(catalog_info, catalog_pixels)
    assert len(catalog.get_healpix_pixels()) == len(catalog_pixels)
    assert len(catalog.pixel_tree.root_pixel.get_all_leaf_descendants()) == len(catalog_pixels)
    for pixel in catalog_pixels:
        assert pixel in catalog.pixel_tree
        assert catalog.pixel_tree[pixel].node_type == PixelNodeType.LEAF


def test_wrong_pixel_input_type(catalog_info):
    with pytest.raises(TypeError):
        Catalog(catalog_info, "test")
    with pytest.raises(TypeError):
        Catalog._get_pixel_tree_from_pixels("test")
    with pytest.raises(TypeError):
        Catalog._get_partition_info_from_pixels("test")


def test_get_pixels_list(catalog_info, catalog_pixels):
    catalog = Catalog(catalog_info, catalog_pixels)
    pixels = catalog.get_healpix_pixels()
    assert pixels == catalog_pixels


def test_load_catalog_small_sky(small_sky_dir):
    """Instantiate a catalog with 1 pixel"""
    cat = Catalog.read_from_hipscat(small_sky_dir)

    assert cat.catalog_name == "small_sky"
    assert len(cat.get_healpix_pixels()) == 1


def test_load_catalog_small_sky_order1(small_sky_order1_dir):
    """Instantiate a catalog with 4 pixels"""
    cat = Catalog.read_from_hipscat(small_sky_order1_dir)

    assert cat.catalog_name == "small_sky_order1"
    assert len(cat.get_healpix_pixels()) == 4


def test_cone_filter(small_sky_order1_catalog):
    filtered_catalog = small_sky_order1_catalog.filter_by_cone(315, -66.443, 0.1)
    filtered_pixels = filtered_catalog.get_healpix_pixels()

    assert len(filtered_pixels) == 1
    assert filtered_pixels == [HealpixPixel(1, 44)]

    assert (1, 44) in filtered_catalog.pixel_tree
    assert len(filtered_catalog.pixel_tree.pixels[1]) == 1
    assert filtered_catalog.catalog_info.total_rows is None


def test_cone_filter_big(small_sky_order1_catalog):
    filtered_catalog = small_sky_order1_catalog.filter_by_cone(315, -66.443, 30)
    assert len(filtered_catalog.get_healpix_pixels()) == 4
    assert (1, 44) in filtered_catalog.pixel_tree
    assert (1, 45) in filtered_catalog.pixel_tree
    assert (1, 46) in filtered_catalog.pixel_tree
    assert (1, 47) in filtered_catalog.pixel_tree


@pytest.mark.timeout(5)
def test_cone_filter_multiple_order(catalog_info):
    catalog_pixel_list = [
        HealpixPixel(6, 30),
        HealpixPixel(7, 124),
        HealpixPixel(7, 5000),
    ]
    catalog = Catalog(catalog_info, catalog_pixel_list)
    filtered_catalog = catalog.filter_by_cone(47.1, 6, 30)
    assert filtered_catalog.get_healpix_pixels() == [HealpixPixel(6, 30), HealpixPixel(7, 124)]


def test_cone_filter_empty(small_sky_order1_catalog):
    filtered_catalog = small_sky_order1_catalog.filter_by_cone(0, 0, 0.1)
    assert len(filtered_catalog.get_healpix_pixels()) == 0
    assert len(filtered_catalog.pixel_tree) == 1


def test_cone_filter_invalid_cone_center(small_sky_order1_catalog):
    with pytest.raises(ValueError, match=ValidatorsErrors.INVALID_DEC):
        small_sky_order1_catalog.filter_by_cone(0, -100, 0.1)
    with pytest.raises(ValueError, match=ValidatorsErrors.INVALID_DEC):
        small_sky_order1_catalog.filter_by_cone(0, 100, 0.1)


def test_polygonal_filter(small_sky_order1_catalog):
    polygon_vertices = [(282, -58), (282, -55), (272, -55), (272, -58)]
    filtered_catalog = small_sky_order1_catalog.filter_by_polygon(polygon_vertices)
    filtered_pixels = filtered_catalog.get_healpix_pixels()
    assert len(filtered_pixels) == 1
    assert filtered_pixels == [HealpixPixel(1, 46)]
    assert (1, 46) in filtered_catalog.pixel_tree
    assert len(filtered_catalog.pixel_tree.pixels[1]) == 1
    assert filtered_catalog.catalog_info.total_rows is None


def test_polygon_filter_with_cartesian_coordinates(small_sky_order1_catalog):
    sky_vertices = [(282, -58), (282, -55), (272, -55), (272, -58)]
    cartesian_vertices = hp.ang2vec(*np.array(sky_vertices).T, lonlat=True)
    filtered_catalog_1 = small_sky_order1_catalog.filter_by_polygon(sky_vertices)
    filtered_catalog_2 = small_sky_order1_catalog.filter_by_polygon(cartesian_vertices)
    assert filtered_catalog_1.get_healpix_pixels() == filtered_catalog_2.get_healpix_pixels()
    assert (1, 46) in filtered_catalog_1.pixel_tree
    assert (1, 46) in filtered_catalog_2.pixel_tree


def test_polygonal_filter_big(small_sky_order1_catalog):
    polygon_vertices = [(281, -69), (281, -25), (350, -25), (350, -69)]
    filtered_catalog = small_sky_order1_catalog.filter_by_polygon(polygon_vertices)
    assert len(filtered_catalog.get_healpix_pixels()) == 4
    assert (1, 44) in filtered_catalog.pixel_tree
    assert (1, 45) in filtered_catalog.pixel_tree
    assert (1, 46) in filtered_catalog.pixel_tree
    assert (1, 47) in filtered_catalog.pixel_tree


def test_polygonal_filter_multiple_order(catalog_info):
    catalog_pixel_list = [
        HealpixPixel(6, 30),
        HealpixPixel(7, 124),
        HealpixPixel(7, 5000),
    ]
    catalog = Catalog(catalog_info, catalog_pixel_list)
    polygon_vertices = [(47.1, 6), (64.5, 6), (64.5, 6.27), (47.1, 6.27)]
    filtered_catalog = catalog.filter_by_polygon(polygon_vertices)
    assert filtered_catalog.get_healpix_pixels() == [HealpixPixel(6, 30), HealpixPixel(7, 124)]


def test_polygonal_filter_empty(small_sky_order1_catalog):
    polygon_vertices = [(0, 0), (1, 1), (0, 2)]
    filtered_catalog = small_sky_order1_catalog.filter_by_polygon(polygon_vertices)
    assert len(filtered_catalog.get_healpix_pixels()) == 0
    assert len(filtered_catalog.pixel_tree) == 1


def test_polygonal_filter_invalid_polygon_coordinates(small_sky_order1_catalog):
    # Declination is over 90 degrees
    polygon_vertices = [(47.1, -100), (64.5, -100), (64.5, 6.27), (47.1, 6.27)]
    with pytest.raises(ValueError, match=ValidatorsErrors.INVALID_DEC):
        small_sky_order1_catalog.filter_by_polygon(polygon_vertices)
    # Right ascension should wrap, it does not throw an error
    polygon_vertices = [(470.1, 6), (470.5, 6), (64.5, 10.27), (47.1, 10.27)]
    small_sky_order1_catalog.filter_by_polygon(polygon_vertices)


def test_empty_directory(tmp_path):
    """Test loading empty or incomplete data"""
    ## Path doesn't exist
    with pytest.raises(FileNotFoundError):
        Catalog.read_from_hipscat(os.path.join("path", "empty"))

    catalog_path = os.path.join(tmp_path, "empty")
    os.makedirs(catalog_path, exist_ok=True)

    ## Path exists but there's nothing there
    with pytest.raises(FileNotFoundError, match="catalog info"):
        Catalog.read_from_hipscat(catalog_path)

    ## catalog_info file exists - getting closer
    file_name = os.path.join(catalog_path, "catalog_info.json")
    with open(file_name, "w", encoding="utf-8") as metadata_file:
        metadata_file.write('{"catalog_name":"empty", "catalog_type":"source"}')

    with pytest.raises(FileNotFoundError, match="metadata"):
        Catalog.read_from_hipscat(catalog_path)

    ## Now we create the needed _metadata and everything is right.
    part_info = PartitionInfo.from_healpix([HealpixPixel(0, 11)])
    part_info.write_to_metadata_files(catalog_path=catalog_path)

    catalog = Catalog.read_from_hipscat(catalog_path)
    assert catalog.catalog_name == "empty"


def test_generate_negative_tree_pixels(small_sky_order1_catalog):
    """Test generate_negative_tree_pixels on a basic catalog."""
    expected_pixels = [
        HealpixPixel(0, 0),
        HealpixPixel(0, 1),
        HealpixPixel(0, 2),
        HealpixPixel(0, 3),
        HealpixPixel(0, 4),
        HealpixPixel(0, 5),
        HealpixPixel(0, 6),
        HealpixPixel(0, 7),
        HealpixPixel(0, 8),
        HealpixPixel(0, 9),
        HealpixPixel(0, 10),
    ]

    negative_tree = small_sky_order1_catalog.generate_negative_tree_pixels()

    assert negative_tree == expected_pixels


def test_generate_negative_tree_pixels_order_0(small_sky_catalog):
    """Test generate_negative_tree_pixels on a catalog with only order 0 pixels."""
    expected_pixels = [
        HealpixPixel(0, 0),
        HealpixPixel(0, 1),
        HealpixPixel(0, 2),
        HealpixPixel(0, 3),
        HealpixPixel(0, 4),
        HealpixPixel(0, 5),
        HealpixPixel(0, 6),
        HealpixPixel(0, 7),
        HealpixPixel(0, 8),
        HealpixPixel(0, 9),
        HealpixPixel(0, 10),
    ]

    negative_tree = small_sky_catalog.generate_negative_tree_pixels()

    assert negative_tree == expected_pixels


def test_generate_negative_tree_pixels_multi_order(small_sky_order1_catalog):
    """Test generate_negative_tree_pixels on a catalog with
    missing pixels on multiple order.
    """
    # remove one of the order 1 pixels from the catalog.
    nodes = small_sky_order1_catalog.pixel_tree.root_pixel.children[0].children
    small_sky_order1_catalog.pixel_tree.root_pixel.children[0].children = nodes[1:]

    expected_pixels = [
        HealpixPixel(0, 0),
        HealpixPixel(0, 1),
        HealpixPixel(0, 2),
        HealpixPixel(0, 3),
        HealpixPixel(0, 4),
        HealpixPixel(0, 5),
        HealpixPixel(0, 6),
        HealpixPixel(0, 7),
        HealpixPixel(0, 8),
        HealpixPixel(0, 9),
        HealpixPixel(0, 10),
        HealpixPixel(1, 44),
    ]

    negative_tree = small_sky_order1_catalog.generate_negative_tree_pixels()

    assert negative_tree == expected_pixels
