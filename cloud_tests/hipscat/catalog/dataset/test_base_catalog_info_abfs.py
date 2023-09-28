import os

from hipscat.catalog.dataset.base_catalog_info import BaseCatalogInfo
from hipscat.io import file_io


def test_read_from_file(base_catalog_info_file_abfs, example_abfs_storage_options, assert_catalog_info_matches_dict):
    base_cat_info_fp = file_io.get_file_pointer_from_path(base_catalog_info_file_abfs)
    catalog_info = BaseCatalogInfo.read_from_metadata_file(base_cat_info_fp, storage_options=example_abfs_storage_options)
    catalog_info_json = file_io.file_io.load_json_file(base_catalog_info_file_abfs, storage_options=example_abfs_storage_options)
    assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
