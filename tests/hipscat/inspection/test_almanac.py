import os

import pytest

from hipscat.inspection.almanac import Almanac


def test_default(almanac_dir, test_data_dir):
    """Test loading from a default directory"""
    os.environ["HIPSCAT_DEFAULT_DIR"] = test_data_dir

    alms = Almanac(include_default_dir=True)
    assert len(alms.catalogs()) == 0

    os.environ["HIPSCAT_ALMANAC_DIR"] = almanac_dir
    alms = Almanac(include_default_dir=True)
    assert len(alms.catalogs()) == 8

    os.environ.pop("HIPSCAT_ALMANAC_DIR")
    alms = Almanac(include_default_dir=True)
    assert len(alms.catalogs()) == 0


def test_non_default(almanac_dir, test_data_dir):
    """Test loading with explicit (non-default) almanac base directory."""
    os.environ["HIPSCAT_DEFAULT_DIR"] = test_data_dir

    alms = Almanac(include_default_dir=False)
    assert len(alms.catalogs()) == 0

    alms = Almanac(include_default_dir=False, dirs=almanac_dir)
    assert len(alms.catalogs()) == 8

    alms = Almanac(include_default_dir=False, dirs=[almanac_dir])
    assert len(alms.catalogs()) == 8

    alms = Almanac(
        include_default_dir=False,
        dirs=[
            os.path.join(almanac_dir, "catalog.yml"),
            os.path.join(almanac_dir, "dataset.yml"),
        ],
    )
    assert len(alms.catalogs()) == 2


def test_namespaced(almanac_dir, test_data_dir):
    """Test that we can add duplicate catalogs, so long as we add a namespace."""
    os.environ["HIPSCAT_ALMANAC_DIR"] = almanac_dir
    os.environ["HIPSCAT_DEFAULT_DIR"] = test_data_dir

    with pytest.warns(match="Duplicate"):
        Almanac(include_default_dir=True, dirs=almanac_dir)

    alms = Almanac(
        include_default_dir=True,
        dirs={"custom": almanac_dir},
    )
    assert len(alms.catalogs()) == 16

    alms = Almanac(
        include_default_dir=False,
        dirs={"custom": almanac_dir, "custom2": almanac_dir},
    )
    assert len(alms.catalogs()) == 16


def test_catalogs_filters(default_almanac):
    """Test listing names of catalogs, using filters"""
    ## all (non-deprecated) catalogs
    assert len(default_almanac.catalogs()) == 8

    ## **all** catalogs
    assert len(default_almanac.catalogs(include_deprecated=True)) == 9

    ## all object and source (skip association/index/etc)
    assert len(default_almanac.catalogs(include_deprecated=True, types=["object", "source"])) == 6

    ## all active object and source
    assert len(default_almanac.catalogs(types=["object", "source"])) == 5

    ## non-existent type
    assert len(default_almanac.catalogs(types=["foo"])) == 0


def test_linked_catalogs_object(default_almanac):
    """Check that we can access the affiliated catalogs"""
    object_almanac = default_almanac.get_almanac_info("small_sky")
    assert len(object_almanac.sources) == 1

    source_almanac = object_almanac.sources[0]
    assert source_almanac.catalog_name == "small_sky_source_catalog"

    source_almanac = default_almanac.get_almanac_info(object_almanac.sources[0].catalog_name)
    assert source_almanac.catalog_name == "small_sky_source_catalog"

    source_catalog = default_almanac.get_catalog(object_almanac.sources[0].catalog_name)
    assert source_catalog.catalog_name == "small_sky_source_catalog"


def test_linked_catalogs_source(default_almanac, test_data_dir):
    """Check that we can access the affiliated catalogs"""
    source_almanac = default_almanac.get_almanac_info("small_sky_source_catalog")
    assert len(source_almanac.objects) == 1

    object_almanac = source_almanac.objects[0]
    assert object_almanac.catalog_name == "small_sky"

    source_almanac = default_almanac.get_almanac_info("small_sky_source_catalog")
    assert len(source_almanac.objects) == 1

    ## This source catalog has no object catalog, *and that's ok*
    new_almanac = Almanac(
        dirs=os.path.join(test_data_dir, "almanac_exception", "standalone_source_catalog.yml")
    )
    source_almanac = new_almanac.get_almanac_info("just_the_small_sky_source_catalog")
    assert len(source_almanac.objects) == 0


def test_linked_catalogs_association(default_almanac):
    """Check that read almanac entries are fully linked to one another."""

    association_almanac = default_almanac.get_almanac_info("small_sky_to_small_sky_order1")
    assert association_almanac.catalog_name == "small_sky_to_small_sky_order1"

    primary_almanac = association_almanac.primary_link
    assert primary_almanac
    assert primary_almanac.catalog_name == "small_sky"
    assert len(primary_almanac.associations) == 1
    assert len(primary_almanac.associations_right) == 0

    join_almanac = association_almanac.join_link
    assert join_almanac
    assert join_almanac.catalog_name == "small_sky_order1"
    assert len(join_almanac.associations) == 0
    assert len(join_almanac.associations_right) == 1


def test_linked_catalogs_index(default_almanac):
    """Check that read almanac entries are fully linked to one another."""

    index_almanac = default_almanac.get_almanac_info("index_catalog")
    assert index_almanac.catalog_name == "index_catalog"

    primary_almanac = index_almanac.primary_link
    assert primary_almanac
    assert primary_almanac.catalog_name == "catalog"
    assert len(primary_almanac.indexes) == 1


def test_linked_catalogs_margin(default_almanac):
    """Check that read almanac entries are fully linked to one another."""

    margin_almanac = default_almanac.get_almanac_info("margin_cache")
    assert margin_almanac.catalog_name == "margin_cache"

    primary_almanac = margin_almanac.primary_link
    assert primary_almanac
    assert primary_almanac.catalog_name == "catalog"
    assert len(primary_almanac.margins) == 1


def test_get_catalog(default_almanac):
    """Test that catalogs in almanac really exist (in test directory)"""

    for catalog_name in default_almanac.catalogs():
        catalog = default_almanac.get_catalog(catalog_name)
        assert catalog
        assert catalog.catalog_name == catalog_name


def test_get_catalog_exceptions(test_data_dir):
    """Test that we can create almanac entries, where catalogs might not exist."""
    bad_catalog_path_file = os.path.join(test_data_dir, "almanac_exception", "bad_catalog_path.yml")

    bad_links = Almanac(include_default_dir=False, dirs=bad_catalog_path_file)
    assert len(bad_links.catalogs()) == 1
    with pytest.raises(FileNotFoundError):
        bad_links.get_catalog("non_existent")


@pytest.mark.parametrize(
    "file_name,expected_error_match",
    [
        ("bad_type.yml", "foo"),
        (
            "association_missing_primary.yml",
            "association table .* missing primary catalog",
        ),
        (
            "association_missing_join.yml",
            "association table .* missing join catalog",
        ),
        (
            "index_missing_primary.yml",
            "index table .* missing primary catalog",
        ),
        (
            "margin_missing_primary.yml",
            "margin table .* missing primary catalog",
        ),
        (
            "bad_primary_path.yml",
            "source catalog .* missing object catalog /does/not/exist",
        ),
    ],
)
def test_almanac_creation(test_data_dir, file_name, expected_error_match):
    """Test that we throw exceptions, where bad almanac data or links exist in the files."""
    bad_links_file = os.path.join(test_data_dir, "almanac_exception", file_name)

    with pytest.warns(match=expected_error_match):
        Almanac(dirs=bad_links_file)
