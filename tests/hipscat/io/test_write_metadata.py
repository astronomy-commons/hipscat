"""Tests of file IO (reads and writes)"""

import shutil
from pathlib import Path

import numpy as np
import numpy.testing as npt
import pytest

import hipscat.io.write_metadata as io
import hipscat.pixel_math as hist
import hipscat.pixel_math.healpix_shim as hp
from hipscat.io import file_io
from hipscat.pixel_math.healpix_pixel import HealpixPixel


def test_write_json_file(assert_text_file_matches, tmp_path):
    """Test of arbitrary json dictionary with strings and numbers"""

    expected_lines = [
        "{\n",
        '    "first_english": "a",',
        '    "first_greek": "alpha",',
        '    "first_number": 1,',
        r'    "first_five_fib": \[',
        "        1,",
        "        1,",
        "        2,",
        "        3,",
        "        5",
        "    ]",
        r'    "integer_type": "<class \'int\'>",',
        '    "np_int": 5000000,',
        '    "np_float": 1.618,',
        '    "pixel": "Order: 5, Pixel: 9000",',
        r'    "pixels": \[',
        '        "Order: 5, Pixel: 9000",',
        '        "Order: 5, Pixel: 9001"',
        "    ]",
        "}",
    ]

    dictionary = {}
    dictionary["first_english"] = "a"
    dictionary["first_greek"] = "alpha"
    dictionary["first_number"] = 1
    dictionary["first_five_fib"] = [1, 1, 2, 3, 5]
    dictionary["integer_type"] = int
    dictionary["np_int"] = np.uint64(5_000_000)
    dictionary["np_float"] = np.float64(1.618)
    dictionary["pixel"] = HealpixPixel(5, 9_000)
    dictionary["pixels"] = np.array([HealpixPixel(5, 9_000), HealpixPixel(5, 9_001)])

    json_filename = tmp_path / "dictionary.json"
    io.write_json_file(dictionary, json_filename)
    assert_text_file_matches(expected_lines, json_filename)


def test_write_json_paths(assert_text_file_matches, tmp_path):
    pathlib_path = Path(tmp_path)
    file_pointer = file_io.FilePointer(tmp_path)
    dictionary = {}
    dictionary["pathlib_path"] = pathlib_path
    dictionary["file_pointer"] = file_pointer
    dictionary["first_greek"] = "alpha"
    expected_lines = [
        "{\n",
        f'    "pathlib_path": "{tmp_path}",',
        f'    "file_pointer": "{tmp_path}",',
        '    "first_greek": "alpha"',
        "}",
    ]
    json_filename = tmp_path / "dictionary.json"
    io.write_json_file(dictionary, json_filename)
    assert_text_file_matches(expected_lines, json_filename)


def test_write_catalog_info(assert_text_file_matches, tmp_path, catalog_info):
    """Test that we accurately write out catalog metadata"""
    catalog_base_dir = tmp_path / "test_name"
    file_io.make_directory(catalog_base_dir)
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

    io.write_catalog_info(dataset_info=catalog_info, catalog_base_dir=catalog_base_dir)
    metadata_filename = catalog_base_dir / "catalog_info.json"
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_provenance_info(assert_text_file_matches, tmp_path, catalog_info):
    """Test that we accurately write out tool-provided generation metadata"""
    catalog_base_dir = tmp_path / "test_name"
    file_io.make_directory(catalog_base_dir)
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
        catalog_base_dir=catalog_base_dir, dataset_info=catalog_info, tool_args=tool_args
    )
    metadata_filename = catalog_base_dir / "provenance_info.json"
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_partition_info_healpix_pixel_map(assert_text_file_matches, tmp_path):
    """Test that we accurately write out the partition stats for overloaded input"""
    catalog_base_dir = tmp_path / "test_name"
    file_io.make_directory(catalog_base_dir)
    expected_lines = [
        "Norder,Dir,Npix,num_rows",
        "0,0,11,131",
    ]
    pixel_map = {HealpixPixel(0, 11): (131, [11])}
    io.write_partition_info(catalog_base_dir, destination_healpix_pixel_map=pixel_map)
    metadata_filename = catalog_base_dir / "partition_info.csv"
    assert_text_file_matches(expected_lines, metadata_filename)

    expected_lines = [
        "Norder,Dir,Npix,num_rows",
        "1,0,44,51",
        "1,0,45,29",
        "1,0,46,51",
    ]
    pixel_map = {
        HealpixPixel(1, 44): (51, [44]),
        HealpixPixel(1, 45): (29, [45]),
        HealpixPixel(1, 46): (51, [46]),
    }
    io.write_partition_info(catalog_base_dir, destination_healpix_pixel_map=pixel_map)
    metadata_filename = catalog_base_dir / "partition_info.csv"
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_partition_info_float(assert_text_file_matches, tmp_path):
    """Test that we accurately write out the individual partition stats
    even when the input is floats instead of ints"""
    catalog_base_dir = tmp_path / "test_name"
    file_io.make_directory(catalog_base_dir)
    expected_lines = [
        "Norder,Dir,Npix,num_rows",
        "0,0,11,131",
    ]
    pixel_map = {HealpixPixel(0.0, 11.0): (131, [44.0, 45.0, 46.0])}
    io.write_partition_info(catalog_base_dir, pixel_map)
    metadata_filename = catalog_base_dir / "partition_info.csv"
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_parquet_metadata(tmp_path, small_sky_dir, small_sky_schema, check_parquet_schema):
    """Copy existing catalog and create new metadata files for it"""
    catalog_base_dir = tmp_path / "catalog"
    shutil.copytree(
        small_sky_dir,
        catalog_base_dir,
    )
    io.write_parquet_metadata(catalog_base_dir)
    check_parquet_schema(catalog_base_dir / "_metadata", small_sky_schema)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        catalog_base_dir / "_common_metadata",
        small_sky_schema,
        0,
    )
    ## Re-write - should still have the same properties.
    io.write_parquet_metadata(catalog_base_dir)
    check_parquet_schema(catalog_base_dir / "_metadata", small_sky_schema)
    ## _common_metadata has 0 row groups
    check_parquet_schema(
        catalog_base_dir / "_common_metadata",
        small_sky_schema,
        0,
    )


def test_read_write_fits_point_map(tmp_path):
    """Check that we write and can read a FITS file for spatial distribution."""
    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]
    io.write_fits_map(tmp_path, initial_histogram)

    output_file = tmp_path / "point_map.fits"

    output = file_io.read_fits_image(output_file)
    npt.assert_array_equal(output, initial_histogram)

    # Check the metadata of the fits file:
    map_fits_image = hp.read_map(output_file, nest=True, h=True)

    header_dict = dict(map_fits_image[1])
    assert header_dict["ORDERING"] == "NESTED"
    assert header_dict["PIXTYPE"] == "HEALPIX"
    assert header_dict["NSIDE"] == 2

    npt.assert_array_equal(initial_histogram, map_fits_image[0])


def test_read_ring_fits_point_map(tmp_path):
    """Check that we write and can read a FITS file for spatial distribution."""
    output_file = tmp_path / "point_map.fits"
    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]
    hp.write_map(output_file, initial_histogram, dtype=np.int64)

    with pytest.warns(UserWarning, match="/hipscat/issues/271"):
        output = file_io.read_fits_image(output_file)
        npt.assert_array_equal(output, initial_histogram)
