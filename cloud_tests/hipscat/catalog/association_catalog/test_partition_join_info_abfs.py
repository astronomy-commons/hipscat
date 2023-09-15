import pandas as pd
import os

from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.io import file_io


def test_read_from_file(example_abfs_path, example_abfs_storage_options, association_catalog_join_pixels):
    association_catalog_partition_join_file = os.path.join(
        example_abfs_path,
        "data",
        "small_sky_to_small_sky_order1",
        "partition_join_info.csv"
    )
    file_pointer = file_io.get_file_pointer_from_path(association_catalog_partition_join_file)
    info = PartitionJoinInfo.read_from_file(file_pointer, storage_options=example_abfs_storage_options)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)
