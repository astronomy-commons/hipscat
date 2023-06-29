import pandas as pd
import pytest

from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.io import file_io


def test_init(association_catalog_join_pixels):
    partition_join_info = PartitionJoinInfo(association_catalog_join_pixels)
    pd.testing.assert_frame_equal(partition_join_info.data_frame, association_catalog_join_pixels)


def test_wrong_columns(association_catalog_join_pixels):
    for column in PartitionJoinInfo.COLUMN_NAMES:
        join_pixels = association_catalog_join_pixels.copy()
        join_pixels = join_pixels.rename(columns={column: "wrong_name"})
        with pytest.raises(ValueError, match=column):
            PartitionJoinInfo(join_pixels)


def test_read_from_file(association_catalog_partition_join_file, association_catalog_join_pixels):
    file_pointer = file_io.get_file_pointer_from_path(association_catalog_partition_join_file)
    info = PartitionJoinInfo.read_from_file(file_pointer)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)
