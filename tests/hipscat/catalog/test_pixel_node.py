import pytest

from hipscat.catalog.pixel_node import PixelNode


def check_node_data_correct(node, node_dict):
    assert node.hp_order == node_dict["hp_order"]
    assert node.hp_pixel == node_dict["hp_pixel"]
    assert node.node_type == node_dict["node_type"]
    assert node.parent == node_dict["parent"]


def test_create_root_node_correct(root_pixel_node_data):
    root_node = PixelNode(**root_pixel_node_data)
    assert root_node
    check_node_data_correct(root_node, root_pixel_node_data)


def test_create_root_node_with_parent_raises_error(root_pixel_node, root_pixel_node_data):
    with pytest.raises(ValueError):
        root_pixel_node_data["parent"] = root_pixel_node
        PixelNode(**root_pixel_node_data)


def test_create_leaf_node(leaf_pixel_node_data, root_pixel_node):
    leaf_node = PixelNode(**leaf_pixel_node_data)
    assert leaf_node
    check_node_data_correct(leaf_node, leaf_pixel_node_data)
    assert len(root_pixel_node.children) == 1
    assert leaf_node in root_pixel_node.children
