import dataclasses
import json

import pytest

from hipscat.catalog.association_catalog.association_catalog_info import (
    AssociationCatalogInfo,
)
from hipscat.io import file_io


def test_association_catalog_info(
    association_catalog_info_data, assert_catalog_info_matches_dict
):
    info = AssociationCatalogInfo(**association_catalog_info_data)
    assert_catalog_info_matches_dict(info, association_catalog_info_data)


def test_str(association_catalog_info_data):
    correct_string = ""
    for name, value in association_catalog_info_data.items():
        correct_string += f"  {name} {value}\n"
    cat_info = AssociationCatalogInfo(**association_catalog_info_data)
    assert str(cat_info) == correct_string


def test_read_from_file(
    association_catalog_info_file, assert_catalog_info_matches_dict
):
    cat_info_fp = file_io.get_file_pointer_from_path(association_catalog_info_file)
    catalog_info = AssociationCatalogInfo.read_from_metadata_file(cat_info_fp)
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

    with open(association_catalog_info_file, "r", encoding="utf-8") as cat_info_file:
        catalog_info_json = json.load(cat_info_file)
        assert_catalog_info_matches_dict(catalog_info, catalog_info_json)


def test_required_fields_missing(association_catalog_info_data):
    for required_field in ["primary_catalog", "join_catalog"]:
        assert required_field in AssociationCatalogInfo.required_fields
    for field in AssociationCatalogInfo.required_fields:
        init_data = association_catalog_info_data.copy()
        init_data[field] = None
        with pytest.raises(ValueError, match=field):
            AssociationCatalogInfo(**init_data)
