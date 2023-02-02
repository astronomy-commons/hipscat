"""Tests of file IO (reads and writes)"""


import os
import tempfile

import file_testing as ft
import numpy as np

import hipscat.io.write_metadata as io
from hipscat.catalog.catalog_parameters import CatalogParameters


def test_write_json_file():
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

    with tempfile.TemporaryDirectory() as tmp_dir:
        json_filename = os.path.join(tmp_dir, "dictionary.json")
        io.write_json_file(dictionary, json_filename)
        ft.assert_text_file_matches(expected_lines, json_filename)


def test_write_catalog_info():
    """Test that we accurately write out catalog metadata"""
    expected_lines = [
        "{",
        '    "catalog_name": "small_sky",',
        r'    "version": "[.\d]+",',  # version matches digits
        r'    "generation_date": "[.\d]+",',  # date matches date format
        '    "ra_kw": "ra",',
        '    "dec_kw": "dec",',
        '    "id_kw": "id",',
        '    "total_objects": 131,',
        '    "origin_healpix_order": 0',
        '    "pixel_threshold": 1000000',
        "}",
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        args = CatalogParameters(
            catalog_name="small_sky",
            input_paths=["foo"],
            input_format="csv",
            output_path=tmp_dir,
            highest_healpix_order=0,
            ra_column="ra",
            dec_column="dec",
        )
        initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])

        io.write_catalog_info(args, initial_histogram)
        metadata_filename = os.path.join(tmp_dir, "small_sky", "catalog_info.json")
        ft.assert_text_file_matches(expected_lines, metadata_filename)


def test_write_partition_info():
    """Test that we accurately write out the individual partition stats"""
    expected_lines = [
        "order,pixel,num_objects",
        "0,11,131",
    ]
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = CatalogParameters(
            catalog_name="small_sky",
            input_paths=["foo"],
            input_format="csv",
            output_path=tmp_dir,
            highest_healpix_order=0,
            ra_column="ra",
            dec_column="dec",
        )
        pixel_map = {tuple([0, 11, 131]): [44, 45, 46]}
        io.write_partition_info(args, pixel_map)
        metadata_filename = os.path.join(tmp_dir, "small_sky", "partition_info.csv")
        ft.assert_text_file_matches(expected_lines, metadata_filename)


def test_write_partition_info_float():
    """Test that we accurately write out the individual partition stats
    even when the input is floats instead of ints"""
    expected_lines = [
        "order,pixel,num_objects",
        "0,11,131",
    ]
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = CatalogParameters(
            catalog_name="small_sky",
            input_paths=["foo"],
            input_format="csv",
            output_path=tmp_dir,
            highest_healpix_order=0,
            ra_column="ra",
            dec_column="dec",
        )
        pixel_map = {tuple([0.0, 11.0, 131.0]): [44.0, 45.0, 46.0]}
        io.write_partition_info(args, pixel_map)
        metadata_filename = os.path.join(tmp_dir, "small_sky", "partition_info.csv")
        ft.assert_text_file_matches(expected_lines, metadata_filename)


def test_write_legacy_metadata_file():
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
    with tempfile.TemporaryDirectory() as tmp_dir:
        args = CatalogParameters(
            catalog_name="small_sky",
            input_paths=["foo"],
            input_format="csv",
            output_path=tmp_dir,
            highest_healpix_order=0,
            ra_column="ra",
            dec_column="dec",
        )
        initial_histogram = np.asarray([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 131])
        pixel_map = np.full(12, None)
        pixel_map[11] = (0, 11, 131)

        io.write_legacy_metadata(args, initial_histogram, pixel_map)

        metadata_filename = os.path.join(tmp_dir, "small_sky", "small_sky_meta.json")

        ft.assert_text_file_matches(expected_lines, metadata_filename)
