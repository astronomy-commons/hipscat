import json
import os

import pytest

from hipscat.catalog.dataset.dataset import Dataset


def test_dataset_init(base_catalog_info):
    dataset = Dataset(base_catalog_info)
    assert dataset.catalog_info == base_catalog_info
    assert dataset.catalog_name == base_catalog_info.catalog_name
    assert not dataset.on_disk
    assert dataset.catalog_path is None
    assert dataset.catalog_base_dir is None


def test_dataset_wrong_catalog_info(base_catalog_info_data):
    with pytest.raises(TypeError, match="catalog_info"):
        Dataset(base_catalog_info_data)


def test_read_from_hipscat(dataset_path, base_catalog_info_file, assert_catalog_info_matches_dict):
    dataset = Dataset.read_from_hipscat(dataset_path)
    assert dataset.on_disk
    assert dataset.catalog_path == dataset_path
    assert str(dataset.catalog_base_dir) == dataset_path
    with open(base_catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(dataset.catalog_info, catalog_info_json)


def test_read_from_missing_folder(tmp_path):
    wrong_path = os.path.join(tmp_path, "wrong")
    with pytest.raises(FileNotFoundError, match="directory"):
        Dataset.read_from_hipscat(wrong_path)


def test_read_from_empty_folder(tmp_path):
    dataset_path = os.path.join(tmp_path, "dat")
    os.makedirs(dataset_path)
    with pytest.raises(FileNotFoundError, match="catalog info"):
        Dataset.read_from_hipscat(dataset_path)
