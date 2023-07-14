import pandas as pd
import pytest

from hipscat.catalog import PartitionInfo
from hipscat.pixel_math import HealpixPixel
from hipscat.pixel_tree.pixel_node import PixelNode
from hipscat.pixel_tree.pixel_node_type import PixelNodeType
from hipscat.pixel_tree.pixel_tree_builder import PixelTreeBuilder


def assert_pixel_tree_has_nodes_in_catalog(tree, catalog):
    """assert tree contains the same nodes as the catalog"""
    assert tree.contains((-1, -1))
    for _, pixel in catalog.get_pixels().iterrows():
        assert tree.contains(
            (
                pixel[PartitionInfo.METADATA_ORDER_COLUMN_NAME],
                pixel[PartitionInfo.METADATA_PIXEL_COLUMN_NAME],
            )
        )


def test_pixel_tree_small_sky(small_sky_catalog, small_sky_pixels):
    """test pixel tree on small sky"""
    pixel_tree = PixelTreeBuilder.from_partition_info_df(small_sky_catalog.get_pixels())
    assert len(pixel_tree) == len(small_sky_catalog.get_pixels()) + 1
    assert_pixel_tree_has_nodes_in_catalog(pixel_tree, small_sky_catalog)
    small_sky_pixel = pixel_tree.get_node(small_sky_pixels[0])
    assert small_sky_pixel.parent == pixel_tree.root_pixel
    assert pixel_tree.root_pixel.node_type == PixelNodeType.ROOT


def test_pixel_tree_small_sky_order1(small_sky_order1_catalog, small_sky_order1_pixels):
    """test pixel tree on small sky order1"""
    pixel_tree = PixelTreeBuilder.from_partition_info_df(small_sky_order1_catalog.get_pixels())
    assert_pixel_tree_has_nodes_in_catalog(pixel_tree, small_sky_order1_catalog)
    first_pixel = pixel_tree.get_node(small_sky_order1_pixels[0])
    second_pixel = pixel_tree.get_node(small_sky_order1_pixels[1])
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
        PixelTreeBuilder.from_partition_info_df(info_with_duplicate)


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
        PixelTreeBuilder.from_partition_info_df(info_with_duplicate)


def test_tree_builder_contains_root_node():
    tree_builder = PixelTreeBuilder()
    assert tree_builder.contains(HealpixPixel(-1, -1))
    assert tree_builder.contains((-1, -1))
    assert (-1, -1) in tree_builder
    assert HealpixPixel(-1, -1) in tree_builder
    assert not tree_builder.contains(HealpixPixel(10, 10))
    assert not tree_builder.contains((10, 10))
    assert (10, 10) not in tree_builder
    assert HealpixPixel(10, 10) not in tree_builder


def test_pixel_builder_contains_added_node():
    tree_builder = PixelTreeBuilder()
    assert not tree_builder.contains((0, 0))
    tree_builder.create_node((0, 0), PixelNodeType.LEAF, tree_builder.root_pixel)
    assert tree_builder.contains((0, 0))


def test_pixel_builder_retrieve_added_node():
    tree_builder = PixelTreeBuilder()
    order = 0
    pixel = 0
    node_type = PixelNodeType.LEAF
    tree_builder.create_node((order, pixel), node_type, tree_builder.root_pixel)
    assert isinstance(tree_builder.get_node((order, pixel)), PixelNode)
    assert tree_builder.get_node((order, pixel)).node_type == node_type
    assert tree_builder.get_node((order, pixel)).parent == tree_builder.root_pixel
    assert tree_builder.get_node((order, pixel)).hp_order == order
    assert tree_builder.get_node((order, pixel)).hp_pixel == pixel
    assert tree_builder.get_node(HealpixPixel(order, pixel)) == tree_builder.get_node((order, pixel))
    assert tree_builder[(order, pixel)] == tree_builder.get_node((order, pixel))
    assert tree_builder[HealpixPixel(order, pixel)] == tree_builder.get_node((order, pixel))


def test_create_node_no_parent_node_errors():
    tree_builder = PixelTreeBuilder()
    with pytest.raises(ValueError, match="no parent node exists"):
        tree_builder.create_node((10, 0), PixelNodeType.LEAF)


def test_create_node_leaf_parent_node_errors():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.LEAF)
    with pytest.raises(ValueError, match="has node type leaf"):
        tree_builder.create_node((1, 0), PixelNodeType.LEAF)


def test_create_node_existing_errors():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.INNER)
    with pytest.raises(ValueError, match="node already exists"):
        tree_builder.create_node((0, 0), PixelNodeType.LEAF)


def test_create_node_replace_existing():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.INNER)
    tree_builder.create_node((1, 0), PixelNodeType.LEAF)
    assert tree_builder[(1, 0)].node_type == PixelNodeType.LEAF
    tree_builder.create_node((1, 0), PixelNodeType.INNER, replace_existing_node=True)
    assert tree_builder[(1, 0)].node_type == PixelNodeType.INNER
    node = tree_builder[(0, 0)]
    tree_builder.create_node((0, 0), PixelNodeType.INNER, replace_existing_node=True)
    assert tree_builder[(0, 0)] is not node
    assert tree_builder[(1, 0)].parent is tree_builder[(0, 0)]
    assert tree_builder[(1, 0)] in tree_builder[(0, 0)].children
    tree_builder.create_node((0, 0), PixelNodeType.LEAF, replace_existing_node=True)
    assert (1, 0) not in tree_builder


def test_pixel_builder_remove_added_node():
    tree_builder = PixelTreeBuilder()
    order = 0
    pixel = 0
    node_type = PixelNodeType.LEAF
    tree_builder.create_node((order, pixel), node_type, tree_builder.root_pixel)
    assert (order, pixel) in tree_builder
    assert order in tree_builder.pixels
    assert len(tree_builder.root_pixel.children) == 1
    assert tree_builder.root_pixel.children[0] == tree_builder[(order, pixel)]
    tree_builder.remove_node((order, pixel))
    assert (order, pixel) not in tree_builder
    assert order not in tree_builder.pixels
    assert len(tree_builder.root_pixel.children) == 0


def test_pixel_builder_remove_nodes_descendents():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.INNER, tree_builder.root_pixel)
    tree_builder.create_node((1, 0), PixelNodeType.INNER)
    tree_builder.create_node((2, 0), PixelNodeType.LEAF)
    for order in [0, 1, 2]:
        assert (order, 0) in tree_builder
        assert order in tree_builder.pixels
    assert len(tree_builder.root_pixel.children) == 1
    assert tree_builder.root_pixel.children[0] == tree_builder[(0, 0)]
    tree_builder.remove_node((0, 0))
    for order in [0, 1, 2]:
        assert (order, 0) not in tree_builder
        assert order not in tree_builder.pixels
    assert len(tree_builder.root_pixel.children) == 0


def test_pixel_builder_not_remove_node_order():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.LEAF)
    tree_builder.create_node((0, 1), PixelNodeType.LEAF)
    assert (0, 0) in tree_builder
    assert (0, 1) in tree_builder
    assert 0 in tree_builder.pixels
    assert len(tree_builder.root_pixel.children) == 2
    assert tree_builder.root_pixel.children[0] == tree_builder[(0, 0)]
    assert tree_builder.root_pixel.children[1] == tree_builder[(0, 1)]
    tree_builder.remove_node((0, 0))
    assert (0, 0) not in tree_builder
    assert (0, 1) in tree_builder
    assert 0 in tree_builder.pixels
    assert len(tree_builder.root_pixel.children) == 1
    assert tree_builder.root_pixel.children[0] == tree_builder[(0, 1)]


def test_remove_missing_node_errors():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.LEAF)
    with pytest.raises(ValueError):
        tree_builder.remove_node((1, 1))


def test_pixel_builder_retrieve_none_node():
    tree_builder = PixelTreeBuilder()
    assert tree_builder.get_node((10, 10)) is None
    assert tree_builder.get_node(HealpixPixel(10, 10)) is None
    assert tree_builder[(10, 10)] is None
    assert tree_builder[HealpixPixel(10, 10)] is None


def test_split_leaf_to_match_partitioning():
    builder1 = PixelTreeBuilder()
    builder2 = PixelTreeBuilder()
    builder1.create_node((0, 0), PixelNodeType.LEAF)
    builder2.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((1, 0), PixelNodeType.INNER)
    builder2.create_node((2, 0), PixelNodeType.LEAF)
    builder1.split_leaf_to_match_partitioning(builder2[(0, 0)])
    assert builder1[(0, 0)].node_type == PixelNodeType.INNER
    assert builder1[(1, 0)].node_type == PixelNodeType.INNER
    for pixel in [(1, 1), (1, 2), (1, 3)]:
        assert pixel in builder1
        assert builder1[pixel].node_type == PixelNodeType.LEAF
    for pixel in [(2, 0), (2, 1), (2, 2), (2, 3)]:
        assert pixel in builder1
        assert builder1[pixel].node_type == PixelNodeType.LEAF


def test_split_leaf_not_exist_errors():
    builder1 = PixelTreeBuilder()
    builder2 = PixelTreeBuilder()
    builder2.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((1, 0), PixelNodeType.INNER)
    builder2.create_node((2, 0), PixelNodeType.LEAF)
    assert (0, 0) not in builder1
    with pytest.raises(ValueError, match="No node in tree"):
        builder1.split_leaf_to_match_partitioning(builder2[(0, 0)])


def test_split_leaf_not_leaf_errors():
    builder1 = PixelTreeBuilder()
    builder2 = PixelTreeBuilder()
    builder1.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((1, 0), PixelNodeType.INNER)
    builder2.create_node((2, 0), PixelNodeType.LEAF)
    assert builder1[(0, 0)].node_type == PixelNodeType.INNER
    with pytest.raises(ValueError, match="is not a leaf node"):
        builder1.split_leaf_to_match_partitioning(builder2[(0, 0)])


def test_add_all_descendants_from_node():
    builder1 = PixelTreeBuilder()
    builder2 = PixelTreeBuilder()
    builder1.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((1, 0), PixelNodeType.INNER)
    builder2.create_node((1, 1), PixelNodeType.LEAF)
    builder2.create_node((2, 0), PixelNodeType.LEAF)
    builder1.add_all_descendants_from_node(builder2[(0, 0)])
    for pixel in [(1, 0), (1, 1), (2, 0)]:
        assert pixel in builder1
        assert builder1[pixel].node_type == builder2[pixel].node_type


def test_add_all_descendants_from_node_missing_node_errors():
    builder1 = PixelTreeBuilder()
    builder2 = PixelTreeBuilder()
    builder2.create_node((0, 0), PixelNodeType.INNER)
    builder2.create_node((1, 0), PixelNodeType.INNER)
    builder2.create_node((2, 0), PixelNodeType.LEAF)
    assert (0, 0) not in builder1
    with pytest.raises(ValueError, match="No node in tree"):
        builder1.add_all_descendants_from_node(builder2[(0, 0)])


def test_built_pixel_tree_contains_same_nodes_as_builder():
    tree_builder = PixelTreeBuilder()
    tree_builder.create_node((0, 0), PixelNodeType.INNER, tree_builder.root_pixel)
    tree_builder.create_node((1, 1), PixelNodeType.LEAF, tree_builder[(0, 0)])
    tree = tree_builder.build()
    for order, nodes_at_order in tree_builder.pixels.items():
        for pixel, node in nodes_at_order.items():
            assert tree.get_node((order, pixel)) == node
            assert tree_builder.get_node((order, pixel)) == node
