import dataclasses
import os

from hipscat.catalog.association_catalog.association_catalog_info import AssociationCatalogInfo
from hipscat.io import file_io


def test_read_from_file(
    association_catalog_info_file_cloud, example_cloud_storage_options, assert_catalog_info_matches_dict
):
    cat_info_fp = file_io.get_file_pointer_from_path(association_catalog_info_file_cloud)
    catalog_info = AssociationCatalogInfo.read_from_metadata_file(
        cat_info_fp, storage_options=example_cloud_storage_options
    )
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "primary_column",
        "primary_catalog",
        "join_column",
        "join_catalog",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    catalog_info_json = file_io.file_io.load_json_file(
        association_catalog_info_file_cloud, storage_options=example_cloud_storage_options
    )
    assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
