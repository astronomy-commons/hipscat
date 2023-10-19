import dataclasses
import os

from hipscat.catalog.index.index_catalog_info import IndexCatalogInfo
from hipscat.io import file_io


def test_read_from_file(
    index_catalog_info_file_cloud, example_cloud_storage_options, assert_catalog_info_matches_dict
):
    cat_info_fp = file_io.get_file_pointer_from_path(index_catalog_info_file_cloud)
    catalog_info = IndexCatalogInfo.read_from_metadata_file(
        cat_info_fp, storage_options=example_cloud_storage_options
    )
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "primary_catalog",
        "indexing_column",
        "extra_columns",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    catalog_info_json = file_io.file_io.load_json_file(
        index_catalog_info_file_cloud, storage_options=example_cloud_storage_options
    )
    assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
