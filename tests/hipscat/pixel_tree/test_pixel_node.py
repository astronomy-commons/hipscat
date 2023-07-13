import pytest

from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_node import PixelNode


def check_node_data_correct(node, node_dict):
    assert node.pixel == node_dict["pixel"]
    assert node.node_type == node_dict["node_type"]
    assert node.parent == node_dict["parent"]


def test_create_root_node(root_pixel_node_data):
    root_node = PixelNode(**root_pixel_node_data)
    assert root_node
    check_node_data_correct(root_node, root_pixel_node_data)


def test_create_root_node_with_parent_raises_error(root_pixel_node, root_pixel_node_data):
    with pytest.raises(ValueError):
        root_pixel_node_data["parent"] = root_pixel_node
        PixelNode(**root_pixel_node_data)


def test_create_root_node_with_wrong_order_raises_error(root_pixel_node_data):
    with pytest.raises(ValueError):
        root_pixel_node_data["pixel"] = HealpixPixel(1, root_pixel_node_data["pixel"].pixel)
        PixelNode(**root_pixel_node_data)


def test_create_inner_node(inner_pixel_node_data, root_pixel_node):
    leaf_node = PixelNode(**inner_pixel_node_data)
    assert leaf_node
    check_node_data_correct(leaf_node, inner_pixel_node_data)
    assert len(root_pixel_node.children) == 1
    assert leaf_node in root_pixel_node.children


def test_create_inner_node_with_no_parent_raises_error(inner_pixel_node_data):
    with pytest.raises(ValueError):
        inner_pixel_node_data["parent"] = None
        PixelNode(**inner_pixel_node_data)


def test_create_leaf_node(leaf_pixel_node_data, inner_pixel_node):
    leaf_node = PixelNode(**leaf_pixel_node_data)
    assert leaf_node
    check_node_data_correct(leaf_node, leaf_pixel_node_data)
    assert len(inner_pixel_node.children) == 1
    assert leaf_node in inner_pixel_node.children


def test_create_leaf_node_with_no_parent_raises_error(leaf_pixel_node_data):
    with pytest.raises(ValueError):
        leaf_pixel_node_data["parent"] = None
        PixelNode(**leaf_pixel_node_data)


def test_create_leaf_node_with_negative_hp_order_raises_error(leaf_pixel_node_data):
    with pytest.raises(ValueError):
        leaf_pixel_node_data["pixel"] = HealpixPixel(-1, leaf_pixel_node_data["pixel"].pixel)
        PixelNode(**leaf_pixel_node_data)


def test_create_leaf_node_with_negative_hp_pixel_raises_error(leaf_pixel_node_data):
    with pytest.raises(ValueError):
        leaf_pixel_node_data["pixel"] = HealpixPixel(leaf_pixel_node_data["pixel"].order, -1)
        PixelNode(**leaf_pixel_node_data)


def test_create_node_with_wrong_order_parent_raises_error(leaf_pixel_node_data, root_pixel_node):
    with pytest.raises(ValueError):
        leaf_pixel_node_data["parent"] = root_pixel_node
        PixelNode(**leaf_pixel_node_data)


def test_add_child_node_with_wrong_child_parent_raises_error(leaf_pixel_node, root_pixel_node):
    with pytest.raises(ValueError):
        root_pixel_node.add_child_node(leaf_pixel_node)


def test_add_max_children_to_root_node(inner_pixel_node_data):
    inner_nodes = []
    for _ in range(12):
        inner_pixel_node_data["pixel"] = HealpixPixel(
            inner_pixel_node_data["pixel"].order,
            inner_pixel_node_data["pixel"].pixel + 1,
        )
        inner_nodes.append(PixelNode(**inner_pixel_node_data))


def test_add_too_many_children_to_root_node_fails(inner_pixel_node_data):
    with pytest.raises(OverflowError):
        inner_nodes = []
        for _ in range(13):
            inner_pixel_node_data["pixel"] = HealpixPixel(
                inner_pixel_node_data["pixel"].order,
                inner_pixel_node_data["pixel"].pixel + 1,
            )
            inner_nodes.append(PixelNode(**inner_pixel_node_data))


def test_add_max_children_to_inner_node(leaf_pixel_node_data):
    leaf_nodes = []
    for _ in range(4):
        leaf_pixel_node_data["pixel"] = HealpixPixel(
            leaf_pixel_node_data["pixel"].order, leaf_pixel_node_data["pixel"].pixel + 1
        )

        leaf_nodes.append(PixelNode(**leaf_pixel_node_data))


def test_add_too_many_children_to_inner_node_fails(leaf_pixel_node_data):
    with pytest.raises(OverflowError):
        leaf_nodes = []
        for _ in range(5):
            leaf_pixel_node_data["pixel"] = HealpixPixel(
                leaf_pixel_node_data["pixel"].order,
                leaf_pixel_node_data["pixel"].pixel + 1,
            )

            leaf_nodes.append(PixelNode(**leaf_pixel_node_data))


def test_add_child_to_leaf_node_fails(leaf_pixel_node, leaf_pixel_node_data):
    with pytest.raises(OverflowError):
        leaf_pixel_node_data["pixel"] = HealpixPixel(
            leaf_pixel_node.hp_order + 1, leaf_pixel_node_data["pixel"].pixel
        )

        leaf_pixel_node_data["parent"] = leaf_pixel_node
        PixelNode(**leaf_pixel_node_data)


def test_get_leaf_descendants_with_leaf_node(leaf_pixel_node):
    assert leaf_pixel_node.get_all_leaf_descendants() == [leaf_pixel_node]


def test_get_leaf_descendants_with_root_node(root_pixel_node, leaf_pixel_node):
    assert root_pixel_node.get_all_leaf_descendants() == [leaf_pixel_node]


def test_get_leaf_descendants_with_multiple_leafs(root_pixel_node, leaf_pixel_node, leaf_pixel_node_data):
    leaf_pixel_node_data["pixel"] = HealpixPixel(
        leaf_pixel_node_data["pixel"].order, leaf_pixel_node_data["pixel"].pixel + 1
    )
    second_leaf = PixelNode(**leaf_pixel_node_data)
    assert root_pixel_node.get_all_leaf_descendants() == [leaf_pixel_node, second_leaf]


def test_remove_child_link(root_pixel_node, inner_pixel_node):
    assert inner_pixel_node in root_pixel_node.children
    assert len(root_pixel_node.children) == 1
    root_pixel_node.remove_child_link(inner_pixel_node)
    assert inner_pixel_node not in root_pixel_node.children
    assert len(root_pixel_node.children) == 0


def test_remove_child_link_wrong_node_errors(root_pixel_node, leaf_pixel_node):
    assert leaf_pixel_node not in root_pixel_node.children
    with pytest.raises(ValueError):
        leaf_pixel_node.remove_child_link(leaf_pixel_node)
