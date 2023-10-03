from hipscat.catalog.dataset.catalog_info_factory import from_catalog_dir
from hipscat.io import get_catalog_info_pointer, get_partition_info_pointer
from hipscat.io.file_io.file_pointer import FilePointer, is_regular_file


def is_valid_catalog(pointer: FilePointer) -> bool:
    """Checks if a catalog is valid for a given base catalog pointer

    Args:
        pointer: pointer to base catalog directory

    Returns:
        True if the catalog_info and partition_info files exist for
        the catalog and the catalog_info file is correctly formatted,
        False otherwise
    """
    catalog_info_pointer = get_catalog_info_pointer(pointer)
    catalog_info_exists = is_regular_file(catalog_info_pointer)

    # Load info to make sure format is correct
    from_catalog_dir(pointer)

    partition_info_pointer = get_partition_info_pointer(pointer)
    partition_info_exists = is_regular_file(partition_info_pointer)

    return catalog_info_exists and partition_info_exists
