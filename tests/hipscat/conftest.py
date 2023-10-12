import pytest

from hipscat.catalog import Catalog
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType

# pylint: disable= redefined-outer-name


@pytest.fixture
def root_pixel_node_data():
    return {
        "pixel": HealpixPixel(-1, -1),
        "node_type": PixelNodeType.ROOT,
        "parent": None,
    }


@pytest.fixture
def root_pixel_node(root_pixel_node_data):
    return PixelNode(**root_pixel_node_data)


@pytest.fixture
def inner_pixel_node_data(root_pixel_node):
    return {
        "pixel": HealpixPixel(0, 1),
        "node_type": PixelNodeType.INNER,
        "parent": root_pixel_node,
    }


@pytest.fixture
def inner_pixel_node(inner_pixel_node_data):
    return PixelNode(**inner_pixel_node_data)


@pytest.fixture
def leaf_pixel_node_data(inner_pixel_node):
    return {
        "pixel": HealpixPixel(1, 12),
        "node_type": PixelNodeType.LEAF,
        "parent": inner_pixel_node,
    }


@pytest.fixture
def leaf_pixel_node(leaf_pixel_node_data):
    return PixelNode(**leaf_pixel_node_data)


@pytest.fixture
def small_sky_catalog(small_sky_dir):
    return Catalog.read_from_hipscat(small_sky_dir)


@pytest.fixture()
def small_sky_pixels():
    return [
        HealpixPixel(0, 11),
    ]


@pytest.fixture
def small_sky_order1_catalog(small_sky_order1_dir):
    return Catalog.read_from_hipscat(small_sky_order1_dir)


@pytest.fixture()
def small_sky_order1_pixels():
    return [
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]
