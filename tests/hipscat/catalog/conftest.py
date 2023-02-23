import pytest

from hipscat.catalog import Catalog
from hipscat.catalog.pixel_node import PixelNode
from hipscat.catalog.pixel_node_type import PixelNodeType

# pylint: disable=missing-function-docstring, redefined-outer-name


@pytest.fixture
def root_pixel_node_data():
    return {
        "hp_order": -1,
        "hp_pixel": -1,
        "node_type": PixelNodeType.ROOT,
        "parent": None,
        "children": None,
    }


@pytest.fixture
def root_pixel_node(root_pixel_node_data):
    return PixelNode(**root_pixel_node_data)


@pytest.fixture
def inner_pixel_node_data(root_pixel_node):
    return {
        "hp_order": 0,
        "hp_pixel": 1,
        "node_type": PixelNodeType.INNER,
        "parent": root_pixel_node,
        "children": None,
    }


@pytest.fixture
def inner_pixel_node(inner_pixel_node_data):
    return PixelNode(**inner_pixel_node_data)


@pytest.fixture
def leaf_pixel_node_data(inner_pixel_node):
    return {
        "hp_order": 1,
        "hp_pixel": 12,
        "node_type": PixelNodeType.LEAF,
        "parent": inner_pixel_node,
        "children": None,
    }


@pytest.fixture
def leaf_pixel_node(leaf_pixel_node_data):
    return PixelNode(**leaf_pixel_node_data)


@pytest.fixture
def small_sky_catalog(small_sky_dir):
    return Catalog(small_sky_dir)


@pytest.fixture()
def small_sky_pixels():
    return [
        {"hp_order": 0, "hp_pixel": 11},
    ]


@pytest.fixture
def small_sky_order1_catalog(small_sky_order1_dir):
    return Catalog(small_sky_order1_dir)


@pytest.fixture()
def small_sky_order1_pixels():
    return [
        {"hp_order": 1, "hp_pixel": 44},
        {"hp_order": 1, "hp_pixel": 45},
        {"hp_order": 1, "hp_pixel": 46},
        {"hp_order": 1, "hp_pixel": 47},
    ]
