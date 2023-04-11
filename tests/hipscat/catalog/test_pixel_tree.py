import pandas as pd
import pytest

from hipscat.catalog import PartitionInfo
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree import PixelTree


def assert_pixel_tree_has_nodes_in_catalog(tree, catalog):
    """assert tree contains the same nodes as the catalog"""
    assert tree.contains(-1, -1)
    for _, pixel in catalog.get_pixels().iterrows():
        assert tree.contains(
            pixel[PartitionInfo.METADATA_ORDER_COLUMN_NAME],
            pixel[PartitionInfo.METADATA_PIXEL_COLUMN_NAME],
        )


def test_pixel_tree_small_sky(small_sky_catalog, small_sky_pixels):
    """test pixel tree on small sky"""
    pixel_tree = PixelTree(small_sky_catalog.get_pixels())
    assert len(pixel_tree) == len(small_sky_catalog.get_pixels()) + 1
    assert_pixel_tree_has_nodes_in_catalog(pixel_tree, small_sky_catalog)
    small_sky_pixel = pixel_tree.get_node(**small_sky_pixels[0])
    assert small_sky_pixel.parent == pixel_tree.root_pixel
    assert pixel_tree.root_pixel.node_type == PixelNodeType.ROOT


def test_pixel_tree_small_sky_order1(small_sky_order1_catalog, small_sky_order1_pixels):
    """test pixel tree on small sky order1"""
    pixel_tree = PixelTree(small_sky_order1_catalog.get_pixels())
    assert_pixel_tree_has_nodes_in_catalog(pixel_tree, small_sky_order1_catalog)
    first_pixel = pixel_tree.get_node(**small_sky_order1_pixels[0])
    second_pixel = pixel_tree.get_node(**small_sky_order1_pixels[1])
    parent_node = first_pixel.parent
    assert parent_node.node_type == PixelNodeType.INNER
    assert first_pixel.parent == second_pixel.parent
    assert parent_node.parent == pixel_tree.root_pixel


def test_duplicate_pixel_raises_error(small_sky_catalog):
    """test pixel tree raises error with duplicate pixels"""
    partition_info = small_sky_catalog.get_pixels()
    pixel_row = partition_info.iloc[0]
    info_with_duplicate = pd.concat([partition_info, pixel_row.to_frame().T])
    with pytest.raises(ValueError):
        PixelTree(info_with_duplicate)


def test_pixel_duplicated_at_different_order_raises_error(small_sky_catalog):
    """test pixel tree raises error with duplicate pixels at different orders"""
    partition_info = small_sky_catalog.get_pixels()
    pixel_row = partition_info.iloc[0].copy()
    pixel_row[PartitionInfo.METADATA_ORDER_COLUMN_NAME] += 1
    pixel_row[PartitionInfo.METADATA_PIXEL_COLUMN_NAME] = (
        pixel_row[PartitionInfo.METADATA_PIXEL_COLUMN_NAME] << 2
    )
    info_with_duplicate = pd.concat([partition_info, pixel_row.to_frame().T])
    with pytest.raises(ValueError):
        PixelTree(info_with_duplicate)
