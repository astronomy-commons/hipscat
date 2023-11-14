from hipscat.catalog.dataset.catalog_info_factory import from_catalog_dir
from hipscat.io import get_partition_info_pointer, get_parquet_metadata_pointer
from hipscat.io.file_io.file_pointer import FilePointer, is_regular_file


def is_valid_catalog(pointer: FilePointer) -> bool:
    """Checks if a catalog is valid for a given base catalog pointer

    Args:
        pointer: pointer to base catalog directory

    Returns:
        True if both the catalog_info and partition_info files are
        valid, False otherwise
    """
    return is_catalog_info_valid(pointer) and (is_partition_info_valid(pointer) or is_metadata_valid(pointer))


def is_catalog_info_valid(pointer):
    """Checks if catalog_info is valid for a given base catalog pointer

    Args:
        pointer: pointer to base catalog directory

    Returns:
        True if the catalog_info file exists, and it is correctly formatted,
        False otherwise
    """
    is_valid = True
    try:
        from_catalog_dir(pointer)
    except (FileNotFoundError, ValueError, NotImplementedError):
        is_valid = False
    return is_valid


def is_partition_info_valid(pointer):
    """Checks if partition_info is valid for a given base catalog pointer

    Args:
        pointer: pointer to base catalog directory

    Returns:
        True if the partition_info file exists, False otherwise
    """
    partition_info_pointer = get_partition_info_pointer(pointer)
    partition_info_exists = is_regular_file(partition_info_pointer)
    return partition_info_exists


def is_metadata_valid(pointer):
    """Checks if _metadata is valid for a given base catalog pointer

    Args:
        pointer: pointer to base catalog directory

    Returns:
        True if the _metadata file exists, False otherwise
    """
    metadata_file = get_parquet_metadata_pointer(pointer)
    metadata_file_exists = is_regular_file(metadata_file)
    return metadata_file_exists
