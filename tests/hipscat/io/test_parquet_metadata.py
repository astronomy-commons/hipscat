"""Tests of file IO (reads and writes)"""

import os
import shutil

import numpy.testing as npt
import pandas as pd
import pyarrow as pa

import hipscat.io.parquet_metadata as io
from hipscat.io import file_io


def test_write_parquet_metadata(tmp_path, small_sky_dir, basic_catalog_parquet_metadata):
    """Copy existing catalog and create new metadata files for it"""
    catalog_base_dir = os.path.join(tmp_path, "catalog")
    shutil.copytree(
        small_sky_dir,
        catalog_base_dir,
    )
    io.write_parquet_metadata(catalog_base_dir)
    check_parquet_schema(os.path.join(catalog_base_dir, "_metadata"), basic_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
    )
    ## Re-write - should still have the same properties.
    io.write_parquet_metadata(catalog_base_dir)
    check_parquet_schema(os.path.join(catalog_base_dir, "_metadata"), basic_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
    )


def test_write_parquet_metadata_order1(tmp_path, small_sky_order1_dir, basic_catalog_parquet_metadata):
    """Copy existing catalog and create new metadata files for it,
    using a catalog with multiple files."""
    temp_path = os.path.join(tmp_path, "catalog")
    shutil.copytree(
        small_sky_order1_dir,
        temp_path,
    )

    io.write_parquet_metadata(temp_path)
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


def test_write_index_parquet_metadata(tmp_path):
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

    io.write_parquet_metadata(temp_path)
    check_parquet_schema(os.path.join(tmp_path, "index", "_metadata"), index_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(tmp_path, "index", "_common_metadata"),
        index_catalog_parquet_metadata,
        0,
    )


def check_parquet_schema(file_name, expected_schema, expected_num_row_groups=1):
    """Check parquet schema against expectations"""
    assert file_io.does_file_or_directory_exist(file_name), f"file not found [{file_name}]"

    single_metadata = file_io.read_parquet_metadata(file_name)
    schema = single_metadata.schema.to_arrow_schema()

    assert len(schema) == len(
        expected_schema
    ), f"object list not the same size ({len(schema)} vs {len(expected_schema)})"

    npt.assert_array_equal(schema.names, expected_schema.names)

    assert schema.equals(expected_schema, check_metadata=False)

    parquet_file = file_io.read_parquet_file(file_name)
    assert parquet_file.metadata.num_row_groups == expected_num_row_groups

    for row_index in range(0, parquet_file.metadata.num_row_groups):
        row_md = parquet_file.metadata.row_group(row_index)
        for column_index in range(0, row_md.num_columns):
            column_metadata = row_md.column(column_index)
            assert column_metadata.file_path.endswith(".parquet")
