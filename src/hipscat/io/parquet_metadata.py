"""Utility functions for handling parquet metadata files"""
import tempfile
from typing import List

import numpy as np
import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq

from hipscat.io import file_io, paths
from hipscat.io.file_io.file_pointer import get_fs, strip_leading_slash_for_pyarrow
from hipscat.pixel_math.healpix_pixel import INVALID_PIXEL, HealpixPixel
from hipscat.pixel_math.healpix_pixel_function import get_pixel_argsort


def row_group_stat_single_value(row_group, stat_key: str):
    """Convenience method to find the min and max inside a statistics dictionary,
    and raise an error if they're unequal.

    Args:
        row_group: dataset fragment row group
        stat_key (str): column name of interest.
    Returns:
        The value of the specified row group statistic
    """
    if stat_key not in row_group.statistics:
        raise ValueError(f"row group doesn't have expected key {stat_key}")
    stat_dict = row_group.statistics[stat_key]
    min_val = stat_dict["min"]
    max_val = stat_dict["max"]
    if min_val != max_val:
        raise ValueError(f"stat min != max ({min_val} != {max_val})")
    return min_val


def get_healpix_pixel_from_metadata(metadata) -> HealpixPixel:
    """Get the healpix pixel according to a parquet file's metadata.

    This is determined by the value of Norder and Npix in the table's data"""
    if metadata.num_row_groups <= 0 or metadata.num_columns <= 0:
        raise ValueError("metadata is for empty table")
    order = -1
    pixel = -1
    first_row_group = metadata.row_group(0)
    for i in range(0, first_row_group.num_columns):
        column = first_row_group.column(i)
        if column.path_in_schema == "Norder":
            order = column.statistics.min
        elif column.path_in_schema == "Npix":
            pixel = column.statistics.min

    if order == -1 or pixel == -1:
        raise ValueError("Metadata missing Norder or Npix column")
    return HealpixPixel(order, pixel)


def write_parquet_metadata(catalog_path: str, order_by_healpix=True, storage_options: dict = None, output_path: str = None):
    """Generate parquet metadata, using the already-partitioned parquet files
    for this catalog.

    For more information on the general parquet metadata files, and why we write them, see
    https://arrow.apache.org/docs/python/parquet.html#writing-metadata-and-common-metadata-files

    Args:
        catalog_path (str): base path for the catalog
        order_by_healpix (bool): use False if the dataset is not ordered by healpix pixel
            (e.g. secondary indexes)
        storage_options: dictionary that contains abstract filesystem credentials
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified
    """
    ignore_prefixes = [
        "intermediate",
        "_common_metadata",
        "_metadata",
    ]

    dataset = file_io.read_parquet_dataset(
        catalog_path,
        storage_options=storage_options,
        ignore_prefixes=ignore_prefixes,
        exclude_invalid_files=True,
    )
    metadata_collector = []
    # Collect the healpix pixels so we can sort before writing.
    healpix_pixels = []

    for hips_file in dataset.files:
        hips_file_pointer = file_io.get_file_pointer_from_path(hips_file, include_protocol=catalog_path)
        single_metadata = file_io.read_parquet_metadata(hips_file_pointer, storage_options=storage_options)

        # Users must set the file path of each chunk before combining the metadata.
        relative_path = hips_file[len(catalog_path) :]
        single_metadata.set_file_path(relative_path)

        if order_by_healpix:
            healpix_pixel = paths.get_healpix_from_path(relative_path)
            if healpix_pixel == INVALID_PIXEL:
                healpix_pixel = get_healpix_pixel_from_metadata(single_metadata)

            healpix_pixels.append(healpix_pixel)
        metadata_collector.append(single_metadata)

    ## Write out the two metadata files
    if output_path is None:
        output_path = catalog_path
    if order_by_healpix:
        argsort = get_pixel_argsort(healpix_pixels)
        metadata_collector = np.array(metadata_collector)[argsort]
    catalog_base_dir = file_io.get_file_pointer_from_path(output_path)
    metadata_file_pointer = paths.get_parquet_metadata_pointer(catalog_base_dir)
    common_metadata_file_pointer = paths.get_common_metadata_pointer(catalog_base_dir)

    file_io.write_parquet_metadata(
        dataset.schema,
        metadata_file_pointer,
        metadata_collector=metadata_collector,
        write_statistics=True,
        storage_options=storage_options,
    )
    file_io.write_parquet_metadata(
        dataset.schema, common_metadata_file_pointer, storage_options=storage_options
    )


def write_parquet_metadata_for_batches(
    batches: List[List[pa.RecordBatch]], output_path: str = None, storage_options: dict = None
):
    """Write parquet metadata files for some pyarrow table batches.
    This writes the batches to a temporary parquet dataset using local storage, and
    generates the metadata for the partitioned catalog parquet files.

    Args:
        batches (List[pa.RecordBatch]): create one batch per group of data (partition or row group)
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified
        storage_options: dictionary that contains abstract filesystem credentials
    """

    with tempfile.TemporaryDirectory() as temp_pq_file:
        for batch_list in batches:
            temp_info_table = pa.Table.from_batches(batch_list)
            pq.write_to_dataset(temp_info_table, temp_pq_file)
        write_parquet_metadata(temp_pq_file, storage_options=storage_options, output_path=output_path)


def read_row_group_fragments(metadata_file: str, storage_options: dict = None):
    """Generator for metadata fragment row groups in a parquet metadata file.

    Args:
        metadata_file (str): path to `_metadata` file.
        storage_options: dictionary that contains abstract filesystem credentials
    """
    file_system, dir_pointer = get_fs(file_pointer=metadata_file, storage_options=storage_options)
    dir_pointer = strip_leading_slash_for_pyarrow(dir_pointer, file_system.protocol)
    dataset = pds.parquet_dataset(dir_pointer, filesystem=file_system)

    for frag in dataset.get_fragments():
        for row_group in frag.row_groups:
            yield row_group
