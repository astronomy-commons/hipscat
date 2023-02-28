"""Tests of file IO (reads and writes)"""


import os

import numpy as np

import hipscat.io.write_metadata as io


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
        "}",
    ]

    dictionary = {}
    dictionary["first_english"] = "a"
    dictionary["first_greek"] = "alpha"
    dictionary["first_number"] = 1
    dictionary["first_five_fib"] = [1, 1, 2, 3, 5]

    json_filename = os.path.join(tmp_path, "dictionary.json")
    io.write_json_file(dictionary, json_filename)
    assert_text_file_matches(expected_lines, json_filename)


def test_write_catalog_info(assert_text_file_matches, tmp_path, basic_catalog_info):
    """Test that we accurately write out catalog metadata"""
    expected_lines = [
        "{",
        '    "catalog_name": "small_sky",',
        r'    "version": ".*",',  # version matches digits
        r'    "generation_date": "[.\d]+",',  # date matches date format
        '    "epoch": "J2000",',
        '    "ra_kw": "ra",',
        '    "dec_kw": "dec",',
        '    "id_kw": "id",',
        '    "total_objects": 131,',
        '    "origin_healpix_order": 0',
        '    "pixel_threshold": 1000000',
        "}",
    ]

    initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])

    io.write_catalog_info(basic_catalog_info, initial_histogram)
    metadata_filename = os.path.join(tmp_path, "small_sky", "catalog_info.json")
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_partition_info(assert_text_file_matches, tmp_path, basic_catalog_info):
    """Test that we accurately write out the individual partition stats"""
    expected_lines = [
        "order,pixel,num_objects",
        "0,11,131",
    ]
    pixel_map = {tuple([0, 11, 131]): [44, 45, 46]}
    io.write_partition_info(basic_catalog_info, pixel_map)
    metadata_filename = os.path.join(tmp_path, "small_sky", "partition_info.csv")
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_partition_info_float(
    assert_text_file_matches, tmp_path, basic_catalog_info
):
    """Test that we accurately write out the individual partition stats
    even when the input is floats instead of ints"""
    expected_lines = [
        "order,pixel,num_objects",
        "0,11,131",
    ]
    pixel_map = {tuple([0.0, 11.0, 131.0]): [44.0, 45.0, 46.0]}
    io.write_partition_info(basic_catalog_info, pixel_map)
    metadata_filename = os.path.join(tmp_path, "small_sky", "partition_info.csv")
    assert_text_file_matches(expected_lines, metadata_filename)


def test_write_legacy_metadata_file(
    assert_text_file_matches, tmp_path, basic_catalog_info
):
    """Test that we can write out the older version of the partition metadata"""
    expected_lines = [
        "{",
        '    "cat_name": "small_sky",',
        '    "ra_kw": "ra",',
        '    "dec_kw": "dec",',
        '    "id_kw": "id",',
        '    "n_sources": 131,',
        '    "pix_threshold": 1000000,',
        r'    "urls": \[',
        '        "foo"',
        "    ],",
        '    "hips": {',
        r'        "0": \[',
        "            11",
        "        ]",
        "    }",
        "}",
    ]
    initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])
    pixel_map = np.full(12, None)
    pixel_map[11] = (0, 11, 131)

    io.write_legacy_metadata(basic_catalog_info, initial_histogram, pixel_map)

    metadata_filename = os.path.join(tmp_path, "small_sky", "small_sky_meta.json")

    assert_text_file_matches(expected_lines, metadata_filename)
