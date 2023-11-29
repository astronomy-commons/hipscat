import os

import pandas as pd
import pytest

from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.io import file_io
from hipscat.pixel_math.healpix_pixel import HealpixPixel


def test_init(association_catalog_join_pixels):
    partition_join_info = PartitionJoinInfo(association_catalog_join_pixels)
    pd.testing.assert_frame_equal(partition_join_info.data_frame, association_catalog_join_pixels)


def test_wrong_columns(association_catalog_join_pixels):
    for column in PartitionJoinInfo.COLUMN_NAMES:
        join_pixels = association_catalog_join_pixels.copy()
        join_pixels = join_pixels.rename(columns={column: "wrong_name"})
        with pytest.raises(ValueError, match=column):
            PartitionJoinInfo(join_pixels)


def test_read_from_metadata(association_catalog_join_pixels, association_catalog_path):
    file_pointer = file_io.get_file_pointer_from_path(os.path.join(association_catalog_path, "_metadata"))
    info = PartitionJoinInfo.read_from_file(file_pointer)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)


def test_primary_to_join_map(association_catalog_join_pixels):
    info = PartitionJoinInfo(association_catalog_join_pixels)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)
    pixel_map = info.primary_to_join_map()

    expected = {
        HealpixPixel(0, 11): [
            HealpixPixel(1, 44),
            HealpixPixel(1, 45),
            HealpixPixel(1, 46),
            HealpixPixel(1, 47),
        ]
    }
    assert pixel_map == expected


def test_metadata_file_round_trip(association_catalog_join_pixels, tmp_path):
    info = PartitionJoinInfo(association_catalog_join_pixels)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)
    info.write_to_metadata_files(tmp_path)

    file_pointer = file_io.get_file_pointer_from_path(os.path.join(tmp_path, "_metadata"))
    new_info = PartitionJoinInfo.read_from_file(file_pointer)
    pd.testing.assert_frame_equal(new_info.data_frame, association_catalog_join_pixels)


def test_read_from_csv(association_catalog_partition_join_file, association_catalog_join_pixels):
    file_pointer = file_io.get_file_pointer_from_path(association_catalog_partition_join_file)
    info = PartitionJoinInfo.read_from_csv(file_pointer)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)


def test_read_from_missing_file(tmp_path):
    wrong_path = os.path.join(tmp_path, "wrong")
    file_pointer = file_io.get_file_pointer_from_path(wrong_path)
    with pytest.raises(FileNotFoundError):
        PartitionJoinInfo.read_from_csv(file_pointer)
