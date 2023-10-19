import dataclasses
import os

import pytest

from hipscat.catalog.catalog_type import CatalogType
from hipscat.catalog.margin_cache.margin_cache_catalog_info import MarginCacheCatalogInfo
from hipscat.io import file_io


def test_read_from_file(
    margin_cache_catalog_info_file_cloud, example_cloud_storage_options, assert_catalog_info_matches_dict
):
    cat_info_fp = file_io.get_file_pointer_from_path(margin_cache_catalog_info_file_cloud)
    catalog_info = MarginCacheCatalogInfo.read_from_metadata_file(
        cat_info_fp, storage_options=example_cloud_storage_options
    )
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "primary_catalog",
        "margin_threshold",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    catalog_info_json = file_io.file_io.load_json_file(
        margin_cache_catalog_info_file_cloud, storage_options=example_cloud_storage_options
    )
    assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
