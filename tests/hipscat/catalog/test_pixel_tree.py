import pandas as pd
import pytest

from hipscat.catalog import PixelNodeType
from hipscat.catalog.pixel_tree import PixelTree


def assert_pixel_tree_has_nodes_in_catalog(tree, catalog):
    assert tree.contains(-1, -1)
    for _, pixel in catalog.get_pixels().iterrows():
        assert tree.contains(pixel["order"], pixel["pixel"])


def test_pixel_tree_small_sky(small_sky_catalog, small_sky_pixels):
    pixel_tree = PixelTree(small_sky_catalog.partition_info)
    assert len(pixel_tree) == len(small_sky_catalog.get_pixels()) + 1
    assert_pixel_tree_has_nodes_in_catalog(pixel_tree, small_sky_catalog)
    small_sky_pixel = pixel_tree.get_node(**small_sky_pixels[0])
    assert small_sky_pixel.parent == pixel_tree.root_pixel
    assert pixel_tree.root_pixel.node_type == PixelNodeType.ROOT


def test_pixel_tree_small_sky_order1(small_sky_order1_catalog, small_sky_order1_pixels):
    pixel_tree = PixelTree(small_sky_order1_catalog.partition_info)
    assert_pixel_tree_has_nodes_in_catalog(pixel_tree, small_sky_order1_catalog)
    first_pixel = pixel_tree.get_node(**small_sky_order1_pixels[0])
    second_pixel = pixel_tree.get_node(**small_sky_order1_pixels[1])
    parent_node = first_pixel.parent
    assert parent_node.node_type == PixelNodeType.INNER
    assert first_pixel.parent == second_pixel.parent
    assert parent_node.parent == pixel_tree.root_pixel


def test_duplicate_pixel_raises_error(small_sky_catalog):
    partition_info = small_sky_catalog.partition_info
    pixel_row = partition_info.iloc[0]
    info_with_duplicate = pd.concat([partition_info, pixel_row.to_frame().T])
    with pytest.raises(ValueError):
        PixelTree(info_with_duplicate)


def test_pixel_duplicated_at_different_order_raises_error(small_sky_catalog):
    partition_info = small_sky_catalog.partition_info
    pixel_row = partition_info.iloc[0]
    pixel_row["order"] += 1
    pixel_row["pixel"] = pixel_row["pixel"] << 2
    info_with_duplicate = pd.concat([partition_info, pixel_row.to_frame().T])
    with pytest.raises(ValueError):
        PixelTree(info_with_duplicate)
