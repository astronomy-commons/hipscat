import warnings

import numpy as np
from upath import UPath

import hipscat.pixel_math.healpix_shim as hp
from hipscat.catalog.dataset.catalog_info_factory import from_catalog_dir
from hipscat.catalog.partition_info import PartitionInfo
from hipscat.io import get_common_metadata_pointer, get_parquet_metadata_pointer, get_partition_info_pointer
from hipscat.io.file_io import read_parquet_dataset
from hipscat.io.file_io.file_pointer import is_regular_file
from hipscat.io.paths import get_healpix_from_path
from hipscat.loaders import read_from_hipscat
from hipscat.pixel_math.healpix_pixel import INVALID_PIXEL
from hipscat.pixel_math.healpix_pixel_function import sort_pixels


# pylint: disable=too-many-statements,too-many-locals
def is_valid_catalog(
    pointer: UPath,
    strict: bool = False,
    fail_fast: bool = False,
    verbose: bool = True,
) -> bool:
    """Checks if a catalog is valid for a given base catalog pointer

    Args:
        pointer (UPath): pointer to base catalog directory
        strict (bool): should we perform additional checking that every optional
            file exists, and contains valid, consistent information.
        fail_fast (bool): if performing strict checks, should we return at the first
            failure, or continue and find all problems?
        verbose (bool): if performing strict checks, should we print out counts,
            progress, and approximate sky coverage?

    Returns:
        True if both the catalog_info and partition_info files are
        valid, False otherwise
    """
    if not strict:
        return is_catalog_info_valid(pointer) and (
            is_partition_info_valid(pointer) or is_metadata_valid(pointer)
        )

    if verbose:
        print(f"Validating catalog at path {pointer} ... ")

    is_valid = True

    def handle_error(msg):
        """inline-method to handle repeated logic of raising error or warning and
        continuing."""
        nonlocal fail_fast
        nonlocal is_valid
        nonlocal verbose
        if fail_fast:
            raise ValueError(msg)
        if verbose:
            print(msg)
        else:
            warnings.warn(msg)
        is_valid = False

    if not is_catalog_info_valid(pointer):
        handle_error("catalog_info.json file does not exist or is invalid.")

    if not is_partition_info_valid(pointer):
        handle_error("partition_info.csv file does not exist.")

    if not is_metadata_valid(pointer):
        handle_error("_metadata file does not exist.")

    if not is_common_metadata_valid(pointer):
        handle_error("_common_metadata file does not exist.")

    if not is_valid:
        # Even if we're not failing fast, we need to stop here if the metadata
        # files don't exist.
        return is_valid

    # Load as a catalog object. Confirms that the catalog info matches type.
    catalog = read_from_hipscat(pointer)
    expected_pixels = sort_pixels(catalog.get_healpix_pixels())

    if verbose:
        print(f"Found {len(expected_pixels)} partitions.")

    ## Compare the pixels in _metadata with partition_info.csv
    metadata_file = get_parquet_metadata_pointer(pointer)

    # Use both strategies of reading the partition info: strict and !strict.
    metadata_pixels = sort_pixels(
        PartitionInfo.read_from_file(metadata_file, strict=True).get_healpix_pixels()
    )
    if not np.array_equal(expected_pixels, metadata_pixels):
        handle_error("Partition pixels differ between catalog and _metadata file (strict)")

    metadata_pixels = sort_pixels(
        PartitionInfo.read_from_file(metadata_file, strict=False).get_healpix_pixels()
    )
    if not np.array_equal(expected_pixels, metadata_pixels):
        handle_error("Partition pixels differ between catalog and _metadata file (non-strict)")

    partition_info_file = get_partition_info_pointer(pointer)
    csv_pixels = sort_pixels(PartitionInfo.read_from_csv(partition_info_file).get_healpix_pixels())
    if not np.array_equal(expected_pixels, csv_pixels):
        handle_error("Partition pixels differ between catalog and partition_info.csv file")

    ## Load as parquet dataset. Allow errors, and check pixel set against _metadata
    ignore_prefixes = [
        "_common_metadata",
        "_metadata",
        "catalog_info.json",
        "provenance_info.json",
        "partition_info.csv",
        "point_map.fits",
        "README",
    ]

    # As a side effect, this confirms that we can load the directory as a valid dataset.
    (dataset_path, dataset) = read_parquet_dataset(
        pointer,
        ignore_prefixes=ignore_prefixes,
        exclude_invalid_files=False,
    )

    parquet_path_pixels = []
    for hips_file in dataset.files:
        relative_path = hips_file[len(dataset_path) :]
        healpix_pixel = get_healpix_from_path(relative_path)
        if healpix_pixel == INVALID_PIXEL:
            handle_error(f"Could not derive partition pixel from parquet path: {relative_path}")

        parquet_path_pixels.append(healpix_pixel)

    parquet_path_pixels = sort_pixels(parquet_path_pixels)

    if not np.array_equal(expected_pixels, parquet_path_pixels):
        handle_error("Partition pixels differ between catalog and parquet paths")

    if verbose:
        # Print a few more stats
        pixel_orders = [p.order for p in expected_pixels]
        cov_order, cov_count = np.unique(pixel_orders, return_counts=True)
        area_by_order = [hp.nside2pixarea(hp.order2nside(order), degrees=True) for order in cov_order]
        total_area = (area_by_order * cov_count).sum()
        print(
            f"Approximate coverage is {total_area:0.2f} sq deg, or {total_area/41253*100:0.2f} % of the sky."
        )

    return is_valid


def is_catalog_info_valid(pointer: UPath) -> bool:
    """Checks if catalog_info is valid for a given base catalog pointer

    Args:
        pointer (UPath): pointer to base catalog directory

    Returns:
        True if the catalog_info file exists, and it is correctly formatted,
        False otherwise
    """
    try:
        from_catalog_dir(pointer)
    except (FileNotFoundError, ValueError, NotImplementedError):
        return False
    return True


def is_partition_info_valid(pointer: UPath) -> bool:
    """Checks if partition_info is valid for a given base catalog pointer

    Args:
        pointer (UPath): pointer to base catalog directory

    Returns:
        True if the partition_info file exists, False otherwise
    """
    partition_info_pointer = get_partition_info_pointer(pointer)
    partition_info_exists = is_regular_file(partition_info_pointer)
    return partition_info_exists


def is_metadata_valid(pointer: UPath) -> bool:
    """Checks if _metadata is valid for a given base catalog pointer

    Args:
        pointer (UPath): pointer to base catalog directory

    Returns:
        True if the _metadata file exists, False otherwise
    """
    metadata_file = get_parquet_metadata_pointer(pointer)
    metadata_file_exists = is_regular_file(metadata_file)
    return metadata_file_exists


def is_common_metadata_valid(pointer: UPath) -> bool:
    """Checks if _common_metadata is valid for a given base catalog pointer

    Args:
        pointer (UPath): pointer to base catalog directory

    Returns:
        True if the _common_metadata file exists, False otherwise
    """
    metadata_file = get_common_metadata_pointer(pointer)
    metadata_file_exists = is_regular_file(metadata_file)
    return metadata_file_exists
