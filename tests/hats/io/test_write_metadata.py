"""Tests of file IO (reads and writes)"""

import numpy as np
import numpy.testing as npt
import pytest

import hats.io.write_metadata as io
import hats.pixel_math as hist
import hats.pixel_math.healpix_shim as hp
from hats.io import file_io
from hats.pixel_math.healpix_pixel import HealpixPixel


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

    with pytest.warns(UserWarning, match="/hats/issues/271"):
        output = file_io.read_fits_image(output_file)
        npt.assert_array_equal(output, initial_histogram)
