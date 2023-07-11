import dataclasses
import json

from hipscat.catalog.catalog_info import CatalogInfo
from hipscat.io import file_io


def test_catalog_info(catalog_info_data, assert_catalog_info_matches_dict):
    info = CatalogInfo(**catalog_info_data)
    assert_catalog_info_matches_dict(info, catalog_info_data)


def test_catalog_info_defaults(base_catalog_info_data, assert_catalog_info_matches_dict):
    info = CatalogInfo(**base_catalog_info_data)
    actual_catalog_info = base_catalog_info_data.copy()
    actual_catalog_info["epoch"] = "J2000"
    actual_catalog_info["ra_column"] = "ra"
    actual_catalog_info["dec_column"] = "dec"
    assert_catalog_info_matches_dict(info, actual_catalog_info)


def test_str(catalog_info_data):
    correct_string = ""
    for name, value in catalog_info_data.items():
        correct_string += f"  {name} {value}\n"
    cat_info = CatalogInfo(**catalog_info_data)
    assert str(cat_info) == correct_string


def test_read_from_file(catalog_info_file, assert_catalog_info_matches_dict):
    cat_info_fp = file_io.get_file_pointer_from_path(catalog_info_file)
    catalog_info = CatalogInfo.read_from_metadata_file(cat_info_fp)
    for column in [
        "catalog_name",
        "catalog_type",
        "total_rows",
        "epoch",
        "ra_column",
        "dec_column",
    ]:
        assert column in dataclasses.asdict(catalog_info)

    with open(catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(catalog_info, catalog_info_json)
