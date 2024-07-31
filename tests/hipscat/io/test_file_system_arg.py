"""Special unit test cases where we pass a `file_system` object into 
various I/O calls, and confirm behavior is unchanged.

If you're making i/o changes and want to confirm that they're adequately 
covered, you can check coverage of only tests inside this file with a command
like the following:

> pytest --cov=hipscat --cov-report=html -k test_file_system_arg
"""

import numpy.testing as npt
import pandas as pd
import pytest
from fsspec.implementations.dirfs import DirFileSystem

from hipscat.catalog import PartitionInfo
from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.catalog.dataset import catalog_info_factory
from hipscat.inspection.almanac import Almanac
from hipscat.inspection.almanac_info import AlmanacInfo
from hipscat.io import file_io, paths
from hipscat.io.validation import is_valid_catalog
from hipscat.loaders import read_from_hipscat
from hipscat.pixel_math import HealpixPixel


@pytest.fixture
def dirfs(test_data_dir):
    """Instantiate a single 'directory file system', which wraps another
    file system, but treats the initialized path as the root of the file
    system. This is kind of ideal for unit tests, as we can use the same
    data as other local file system tests, but with passing different
    paths into the calls."""
    return DirFileSystem(test_data_dir)


def test_read_hipscat_with_file_system(dirfs):
    small_sky_catalog = read_from_hipscat("small_sky", file_system=dirfs)

    small_sky_paths = paths.pixel_catalog_files("small_sky", small_sky_catalog.get_healpix_pixels())
    assert len(small_sky_paths) == 1
    frame = file_io.read_parquet_file_to_pandas(small_sky_paths[0], file_system=dirfs)
    assert len(frame) == 131

    assert is_valid_catalog("small_sky", file_system=dirfs)

    read_from_hipscat("small_sky_order1", file_system=dirfs)
    read_from_hipscat("small_sky_to_small_sky_order1", file_system=dirfs)
    read_from_hipscat("small_sky_order1_margin", file_system=dirfs)
    read_from_hipscat("small_sky_source", file_system=dirfs)
    catalog_info_factory.from_catalog_dir(
        catalog_base_dir="small_sky",
        file_system=dirfs,
    )
    index_catalog = read_from_hipscat("small_sky_source_object_index", file_system=dirfs)
    npt.assert_array_equal(index_catalog.loc_partitions([700]), [HealpixPixel(2, 184)])


def test_partition_info_with_file_system(dirfs, association_catalog_join_pixels, tmp_path):
    write_dirfs = DirFileSystem(tmp_path)
    write_dirfs.makedirs("small_sky")
    write_dirfs.makedirs("small_sky_association")

    metadata_file = paths.get_parquet_metadata_pointer("small_sky")
    info = PartitionInfo.read_from_file(metadata_file, file_system=dirfs)
    assert info.get_healpix_pixels() == [HealpixPixel(0, 11)]
    info.write_to_file(catalog_path="small_sky", file_system=write_dirfs)
    info.write_to_metadata_files(catalog_path="small_sky", file_system=write_dirfs)

    info = PartitionInfo.read_from_file(metadata_file, strict=True, file_system=dirfs)
    assert info.get_healpix_pixels() == [HealpixPixel(0, 11)]

    metadata_file = paths.get_parquet_metadata_pointer("small_sky_to_small_sky_order1")
    info = PartitionJoinInfo.read_from_file(metadata_file, file_system=dirfs)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)
    info.write_to_csv(catalog_path="small_sky_association", file_system=write_dirfs)
    info.write_to_metadata_files(catalog_path="small_sky_association", file_system=write_dirfs)


def test_almanac_with_file_system(dirfs, tmp_path):
    """Test loading from a default directory"""
    alms = Almanac(include_default_dir=False, file_system=dirfs, dirs="almanac")
    assert len(alms.catalogs()) == 7

    almanac_info = AlmanacInfo.from_catalog_dir("small_sky", file_system=dirfs)
    assert almanac_info.catalog_name == "small_sky"

    write_dirfs = DirFileSystem(tmp_path)
    almanac_info.write_to_file(directory="", default_dir=False, file_system=write_dirfs)
