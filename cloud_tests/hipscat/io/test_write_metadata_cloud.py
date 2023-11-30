"""Tests of file IO (reads and writes)"""

import os

import numpy.testing as npt
import pytest

import hipscat.io.write_metadata as io
import hipscat.pixel_math as hist
from hipscat.io import file_io
from hipscat.io.parquet_metadata import write_parquet_metadata


def test_write_catalog_info(
    assert_text_file_matches, tmp_dir_cloud, catalog_info, example_cloud_storage_options
):
    """Test that we accurately write out catalog metadata"""
    catalog_base_dir = os.path.join(tmp_dir_cloud, "test_name")
    file_io.make_directory(catalog_base_dir, storage_options=example_cloud_storage_options)
    expected_lines = [
        "{",
        '    "catalog_name": "test_name",',
        '    "catalog_type": "object",',
        '    "total_rows": 10,',
        '    "epoch": "J2000",',
        '    "ra_column": "ra",',
        '    "dec_column": "dec"',
        "}",
    ]

    io.write_catalog_info(
        dataset_info=catalog_info,
        catalog_base_dir=catalog_base_dir,
        storage_options=example_cloud_storage_options,
    )
    metadata_filename = os.path.join(catalog_base_dir, "catalog_info.json")
    assert_text_file_matches(expected_lines, metadata_filename, storage_options=example_cloud_storage_options)


def test_write_provenance_info(
    assert_text_file_matches, tmp_dir_cloud, catalog_info, example_cloud_storage_options
):
    """Test that we accurately write out tool-provided generation metadata"""
    catalog_base_dir = os.path.join(tmp_dir_cloud, "test_name")
    file_io.make_directory(catalog_base_dir, storage_options=example_cloud_storage_options)
    expected_lines = [
        "{",
        '    "catalog_name": "test_name",',
        '    "catalog_type": "object",',
        '    "total_rows": 10,',
        '    "epoch": "J2000",',
        '    "ra_column": "ra",',
        '    "dec_column": "dec",',
        r'    "version": ".*",',  # version matches digits
        r'    "generation_date": "[.\d]+",',  # date matches date format
        '    "tool_args": {',
        '        "tool_name": "hipscat-import",',
        '        "tool_version": "1.0.0",',
        r'        "input_file_names": \[',
        '            "file1",',
        '            "file2",',
        '            "file3"',
        "        ]",
        "    }",
        "}",
    ]

    tool_args = {
        "tool_name": "hipscat-import",
        "tool_version": "1.0.0",
        "input_file_names": ["file1", "file2", "file3"],
    }

    io.write_provenance_info(
        catalog_base_dir=catalog_base_dir,
        dataset_info=catalog_info,
        tool_args=tool_args,
        storage_options=example_cloud_storage_options,
    )
    metadata_filename = os.path.join(catalog_base_dir, "provenance_info.json")
    assert_text_file_matches(expected_lines, metadata_filename, storage_options=example_cloud_storage_options)


@pytest.mark.timeout(20)
def test_write_parquet_metadata(
    tmp_dir_cloud,
    small_sky_dir_cloud,
    basic_catalog_parquet_metadata,
    example_cloud_storage_options,
):
    """Use existing catalog parquet files and create new metadata files for it"""
    catalog_base_dir = os.path.join(tmp_dir_cloud, "small_sky")

    write_parquet_metadata(
        catalog_path=small_sky_dir_cloud,
        storage_options=example_cloud_storage_options,
        output_path=catalog_base_dir,
    )

    check_parquet_schema(
        os.path.join(catalog_base_dir, "_metadata"),
        basic_catalog_parquet_metadata,
        storage_options=example_cloud_storage_options,
    )
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
        storage_options=example_cloud_storage_options,
    )

    ## Re-write - should still have the same properties.
    write_parquet_metadata(
        catalog_path=small_sky_dir_cloud,
        storage_options=example_cloud_storage_options,
        output_path=catalog_base_dir,
    )
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_metadata"),
        basic_catalog_parquet_metadata,
        storage_options=example_cloud_storage_options,
    )
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        os.path.join(catalog_base_dir, "_common_metadata"),
        basic_catalog_parquet_metadata,
        0,
        storage_options=example_cloud_storage_options,
    )


def check_parquet_schema(file_name, expected_schema, expected_num_row_groups=1, storage_options: dict = None):
    """Check parquet schema against expectations"""
    assert file_io.does_file_or_directory_exist(file_name, storage_options=storage_options)

    single_metadata = file_io.read_parquet_metadata(file_name, storage_options=storage_options)
    schema = single_metadata.schema.to_arrow_schema()

    assert len(schema) == len(
        expected_schema
    ), f"object list not the same size ({len(schema)} vs {len(expected_schema)})"

    npt.assert_array_equal(schema.names, expected_schema.names)

    assert schema.equals(expected_schema, check_metadata=False)

    parquet_file = file_io.read_parquet_file(file_pointer=file_name, storage_options=storage_options)
    assert parquet_file.metadata.num_row_groups == expected_num_row_groups

    for row_index in range(0, parquet_file.metadata.num_row_groups):
        row_md = parquet_file.metadata.row_group(row_index)
        for column_index in range(0, row_md.num_columns):
            column_metadata = row_md.column(column_index)
            assert column_metadata.file_path.endswith(".parquet")


def test_read_write_fits_point_map(tmp_dir_cloud, example_cloud_storage_options):
    """Check that we write and can read a FITS file for spatial distribution."""
    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]
    io.write_fits_map(tmp_dir_cloud, initial_histogram, storage_options=example_cloud_storage_options)

    output_file = os.path.join(tmp_dir_cloud, "point_map.fits")

    output = file_io.read_fits_image(output_file, storage_options=example_cloud_storage_options)
    npt.assert_array_equal(output, initial_histogram)
