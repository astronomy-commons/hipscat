import os

import pytest

from hipscat.catalog.dataset.dataset import Dataset
from hipscat.io.file_io import file_io, file_pointer


def test_read_from_hipscat(dataset_path_cloud, base_catalog_info_file_cloud, example_cloud_storage_options, assert_catalog_info_matches_dict):
    dataset = Dataset.read_from_hipscat(dataset_path_cloud, storage_options=example_cloud_storage_options)
    assert dataset.on_disk
    assert dataset.catalog_path == dataset_path_cloud
    assert str(dataset.catalog_base_dir) == dataset_path_cloud
    catalog_info_json = file_io.load_json_file(base_catalog_info_file_cloud, storage_options=example_cloud_storage_options)
    assert_catalog_info_matches_dict(dataset.catalog_info, catalog_info_json)


def test_read_from_missing_folder(tmp_dir_cloud, example_cloud_storage_options):
    wrong_path = os.path.join(tmp_dir_cloud, "wrong")
    with pytest.raises(FileNotFoundError, match="directory"):
        Dataset.read_from_hipscat(wrong_path, storage_options=example_cloud_storage_options)
