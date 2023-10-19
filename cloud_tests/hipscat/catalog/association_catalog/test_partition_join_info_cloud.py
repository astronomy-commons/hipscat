import os

import pandas as pd

from hipscat.catalog.association_catalog.partition_join_info import PartitionJoinInfo
from hipscat.io import file_io


def test_read_from_file(
    association_catalog_partition_join_file_cloud,
    example_cloud_storage_options,
    association_catalog_join_pixels,
):
    file_pointer = file_io.get_file_pointer_from_path(association_catalog_partition_join_file_cloud)
    info = PartitionJoinInfo.read_from_file(file_pointer, storage_options=example_cloud_storage_options)
    pd.testing.assert_frame_equal(info.data_frame, association_catalog_join_pixels)
