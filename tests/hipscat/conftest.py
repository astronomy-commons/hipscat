import pytest

from hipscat.catalog.pixel_node import PixelNode
from hipscat.catalog.pixel_node_type import PixelNodeType


@pytest.fixture
def root_pixel_node_data():
    return {
        "hp_order": None,
        "hp_pixel": None,
        "node_type": PixelNodeType.ROOT,
        "parent": None,
        "children": None,
    }


@pytest.fixture
def root_pixel_node():
    return PixelNode(
        None,
        None,
        PixelNodeType.ROOT,
    )


@pytest.fixture
def leaf_pixel_node_data(root_pixel_node):
    return {
        "hp_order": 0,
        "hp_pixel": 1,
        "node_type": PixelNodeType.LEAF,
        "parent": root_pixel_node,
        "children": None,
    }
