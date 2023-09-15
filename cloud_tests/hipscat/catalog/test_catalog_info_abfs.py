import dataclasses
import os

from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.io import file_io


def test_read_from_file(example_abfs_path, example_abfs_storage_options, assert_catalog_info_matches_dict):
    catalog_info_file = os.path.join(
        example_abfs_path,
        "data", "catalog", "catalog_info.json"
    )
    cat_info_fp = file_io.get_file_pointer_from_path(catalog_info_file)
    catalog_info = CatalogInfo.read_from_metadata_file(cat_info_fp, storage_options=example_abfs_storage_options)
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "epoch",
        "ra_column",
        "dec_column",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    catalog_info_json = file_io.file_io.load_json_file(catalog_info_file, storage_options=example_abfs_storage_options)
    assert_catalog_info_matches_dict(catalog_info, catalog_info_json)