"""Tests of file IO (reads and writes)"""

import os
import shutil

import pandas as pd
import pyarrow as pa
import pytest

from hipscat.io import file_io, paths
from hipscat.io.parquet_metadata import (
    read_row_group_fragments,
    row_group_stat_single_value,
    write_parquet_metadata,
)


def test_write_parquet_metadata(
    tmp_path, small_sky_dir, basic_catalog_parquet_metadata, check_parquet_schema
):
    """Copy existing catalog and create new metadata files for it"""
    catalog_base_dir = os.path.join(tmp_path, "catalog")
    shutil.copytree(
        small_sky_dir,
        catalog_base_dir,
    )
    write_parquet_metadata(catalog_base_dir)
    check_parquet_schema(os.path.join(catalog_base_dir, "_metadata"), basic_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
    )
    ## Re-write - should still have the same properties.
    write_parquet_metadata(catalog_base_dir)
    check_parquet_schema(os.path.join(catalog_base_dir, "_metadata"), basic_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
    )


def test_write_parquet_metadata_order1(
    tmp_path, small_sky_order1_dir, basic_catalog_parquet_metadata, check_parquet_schema
):
    """Copy existing catalog and create new metadata files for it,
    using a catalog with multiple files."""
    temp_path = os.path.join(tmp_path, "catalog")
    shutil.copytree(
        small_sky_order1_dir,
        temp_path,
    )

    write_parquet_metadata(temp_path)
    ## 4 row groups for 4 partitioned parquet files
    check_parquet_schema(
        os.path.join(temp_path, "_metadata"),
        basic_catalog_parquet_metadata,
        4,
    )
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(temp_path, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
    )


def test_write_index_parquet_metadata(tmp_path, check_parquet_schema):
    """Create an index-like catalog, and test metadata creation."""
    temp_path = os.path.join(tmp_path, "index")

    index_parquet_path = os.path.join(temp_path, "Parts=0", "part_000_of_001.parquet")
    file_io.make_directory(os.path.join(temp_path, "Parts=0"))
    basic_index = pd.DataFrame({"_hipscat_id": [4000, 4001], "ps1_objid": [700, 800]})
    file_io.write_dataframe_to_parquet(basic_index, index_parquet_path)

    index_catalog_parquet_metadata = pa.schema(
        [
            pa.field("_hipscat_id", pa.int64()),
            pa.field("ps1_objid", pa.int64()),
        ]
    )

    write_parquet_metadata(temp_path)
    check_parquet_schema(os.path.join(tmp_path, "index", "_metadata"), index_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(tmp_path, "index", "_common_metadata"),
        index_catalog_parquet_metadata,
        0,
    )


def test_row_group_fragments(small_sky_order1_dir):
    partition_info_file = paths.get_parquet_metadata_pointer(small_sky_order1_dir)

    num_row_groups = 0
    for _ in read_row_group_fragments(partition_info_file):
        num_row_groups += 1

    assert num_row_groups == 4


def test_row_group_stats(small_sky_dir):
    partition_info_file = paths.get_parquet_metadata_pointer(small_sky_dir)
    first_row_group = next(read_row_group_fragments(partition_info_file))

    assert row_group_stat_single_value(first_row_group, "Norder") == 0
    assert row_group_stat_single_value(first_row_group, "Npix") == 11

    with pytest.raises(ValueError, match="doesn't have expected key"):
        row_group_stat_single_value(first_row_group, "NOT HERE")

    with pytest.raises(ValueError, match="stat min != max"):
        row_group_stat_single_value(first_row_group, "ra")
