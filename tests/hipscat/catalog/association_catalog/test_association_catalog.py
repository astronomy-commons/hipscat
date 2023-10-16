import json
import os

import pandas as pd
import pytest

from hipscat.catalog import CatalogType, PartitionInfo
from hipscat.catalog.association_catalog.association_catalog import AssociationCatalog
from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.pixel_tree.pixel_node_type import PixelNodeType


def test_init_catalog(association_catalog_info, association_catalog_pixels, association_catalog_join_pixels):
    catalog = AssociationCatalog(
        association_catalog_info, [HealpixPixel(0,11)], association_catalog_join_pixels
    )
    assert catalog.catalog_name == association_catalog_info.catalog_name
    pd.testing.assert_frame_equal(catalog.get_join_pixels(), association_catalog_join_pixels)
    pd.testing.assert_frame_equal(catalog.get_pixels(), association_catalog_pixels)
    assert catalog.catalog_info == association_catalog_info

    assert len(catalog.get_healpix_pixels()) == len(association_catalog_pixels)
    for hp_pixel in catalog.get_healpix_pixels():
        assert (
            len(
                association_catalog_pixels.loc[
                    (association_catalog_pixels[PartitionInfo.METADATA_ORDER_COLUMN_NAME] == hp_pixel.order)
                    & (association_catalog_pixels[PartitionInfo.METADATA_PIXEL_COLUMN_NAME] == hp_pixel.pixel)
                ]
            )
            == 1
        )
        assert hp_pixel in catalog.pixel_tree
        assert catalog.pixel_tree[hp_pixel].node_type == PixelNodeType.LEAF


def test_wrong_catalog_type(
    association_catalog_info, association_catalog_pixels, association_catalog_join_pixels
):
    association_catalog_info.catalog_type = CatalogType.OBJECT
    with pytest.raises(ValueError, match="catalog_type"):
        AssociationCatalog(
            association_catalog_info, association_catalog_pixels, association_catalog_join_pixels
        )


def test_wrong_catalog_info_type(catalog_info, association_catalog_pixels, association_catalog_join_pixels):
    catalog_info.catalog_type = CatalogType.ASSOCIATION
    with pytest.raises(TypeError, match="catalog_info"):
        AssociationCatalog(catalog_info, association_catalog_pixels, association_catalog_join_pixels)


def test_wrong_join_pixels_type(association_catalog_info, association_catalog_pixels):
    with pytest.raises(TypeError, match="join_pixels"):
        AssociationCatalog(association_catalog_info, association_catalog_pixels, "test")


def test_different_join_pixels_type(
    association_catalog_info, association_catalog_pixels, association_catalog_join_pixels
):
    partition_join_info = PartitionJoinInfo(association_catalog_join_pixels)
    catalog = AssociationCatalog(association_catalog_info, association_catalog_pixels, partition_join_info)
    pd.testing.assert_frame_equal(catalog.get_join_pixels(), association_catalog_join_pixels)


def test_read_from_file(
    association_catalog_path, association_catalog_pixels, association_catalog_join_pixels
):
    catalog = AssociationCatalog.read_from_hipscat(association_catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == association_catalog_path
    assert len(catalog.get_join_pixels()) == 4
    assert len(catalog.get_pixels()) == 1
    assert len(catalog.get_healpix_pixels()) == 1
    pd.testing.assert_frame_equal(catalog.get_join_pixels(), association_catalog_join_pixels)
    pd.testing.assert_frame_equal(catalog.get_pixels(), association_catalog_pixels)

    info = catalog.catalog_info
    assert info.primary_catalog == "small_sky"
    assert info.primary_column == "id"
    assert info.join_catalog == "small_sky_order1"
    assert info.join_column == "id"


def test_empty_directory(tmp_path, association_catalog_info_data, association_catalog_join_pixels):
    """Test loading empty or incomplete data"""
    ## Path doesn't exist
    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(os.path.join("path", "empty"))

    catalog_path = os.path.join(tmp_path, "empty")
    os.makedirs(catalog_path, exist_ok=True)

    ## Path exists but there's nothing there
    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(catalog_path)

    ## catalog_info file exists - getting closer
    file_name = os.path.join(catalog_path, "catalog_info.json")
    with open(file_name, "w", encoding="utf-8") as metadata_file:
        metadata_file.write(json.dumps(association_catalog_info_data))

    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(catalog_path)

    ## partition_info file exists - almost there
    file_name = os.path.join(catalog_path, "partition_info.csv")
    with open(file_name, "w", encoding="utf-8") as metadata_file:
        metadata_file.write("foo")

    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(catalog_path)

    ## partition_join info file exists - enough to create a catalog
    file_name = os.path.join(catalog_path, "partition_join_info.csv")
    association_catalog_join_pixels.to_csv(file_name)

    catalog = AssociationCatalog.read_from_hipscat(catalog_path)
    assert catalog.catalog_name == association_catalog_info_data["catalog_name"]
