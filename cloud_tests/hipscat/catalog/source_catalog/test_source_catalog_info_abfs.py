import dataclasses
import os
from hipscat.catalog.source_catalog.source_catalog_info import SourceCatalogInfo
from hipscat.io import file_io

def test_read_from_file(source_catalog_info_file_abfs, example_abfs_storage_options, assert_catalog_info_matches_dict):
    cat_info_fp = file_io.get_file_pointer_from_path(source_catalog_info_file_abfs)
    catalog_info = SourceCatalogInfo.read_from_metadata_file(cat_info_fp, storage_options=example_abfs_storage_options)
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "primary_catalog",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    catalog_info_json = file_io.file_io.load_json_file(source_catalog_info_file_abfs, storage_options=example_abfs_storage_options)
    assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
