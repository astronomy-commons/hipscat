from hipscat.catalog.association_catalog.association_catalog import \
    AssociationCatalog


def test_small_sky_assoc(small_sky_to_small_sky_order1_dir):
    cat = AssociationCatalog.read_from_hipscat(small_sky_to_small_sky_order1_dir)
    print(cat.get_join_pixels())
