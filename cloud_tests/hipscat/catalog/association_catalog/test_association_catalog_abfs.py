import json
import os

import pandas as pd
import pytest

from hipscat.catalog import CatalogType
from hipscat.catalog.association_catalog.association_catalog import AssociationCatalog
from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.io.file_io import file_io, file_pointer

def test_read_from_file(association_catalog_path_abfs, example_abfs_storage_options, association_catalog_join_pixels):
    catalog = AssociationCatalog.read_from_hipscat(association_catalog_path_abfs, storage_options=example_abfs_storage_options)
    assert catalog.on_disk
    assert catalog.catalog_path == association_catalog_path_abfs
    assert len(catalog.get_join_pixels()) == 4
    pd.testing.assert_frame_equal(catalog.get_join_pixels(), association_catalog_join_pixels)

    info = catalog.catalog_info
    assert info.primary_catalog == "small_sky"
    assert info.primary_column == "id"
    assert info.join_catalog == "small_sky_order1"
    assert info.join_column == "id"


def test_empty_directory(tmp_dir_abfs, example_abfs_storage_options, association_catalog_info_data, association_catalog_join_pixels):
    """Test loading empty or incomplete data"""
    empty_path = os.path.join(tmp_dir_abfs, "path", "empty")
    ## Path doesn't exist
    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(empty_path, storage_options=example_abfs_storage_options)

    catalog_path = os.path.join(tmp_dir_abfs, "empty")
    file_io.make_directory(catalog_path, storage_options=example_abfs_storage_options, exist_ok=True)

    ## Path exists but there's nothing there
    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(catalog_path, storage_options=example_abfs_storage_options)

    ## catalog_info file exists - getting closer
    file_name = os.path.join(catalog_path, "catalog_info.json")
    file_io.write_string_to_file(file_pointer=file_name, string=json.dumps(association_catalog_info_data), storage_options=example_abfs_storage_options)

    with pytest.raises(FileNotFoundError):
        AssociationCatalog.read_from_hipscat(catalog_path, storage_options=example_abfs_storage_options)

    ## partition_info file exists - enough to create a catalog
    file_name = os.path.join(catalog_path, "partition_join_info.csv")
    file_io.write_dataframe_to_csv(
        association_catalog_join_pixels,
        file_pointer=file_name,
        storage_options=example_abfs_storage_options
    )

    catalog = AssociationCatalog.read_from_hipscat(catalog_path, storage_options=example_abfs_storage_options)
    assert catalog.catalog_name == association_catalog_info_data["catalog_name"]

    file_io.delete_file(os.path.join(catalog_path, "catalog_info.json"), storage_options=example_abfs_storage_options)
    file_io.delete_file(os.path.join(catalog_path, "partition_join_info.csv"), storage_options=example_abfs_storage_options)
