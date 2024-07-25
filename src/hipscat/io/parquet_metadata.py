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


def get_healpix_pixel_from_metadata(
    metadata: pq.FileMetaData, norder_column: str = "Norder", npix_column: str = "Npix"
) -> HealpixPixel:
    """Get the healpix pixel according to a parquet file's metadata.

    This is determined by the value of Norder and Npix in the table's data

    Args:
        metadata (pyarrow.parquet.FileMetaData): full metadata for a single file.

    Returns:
        Healpix pixel representing the Norder and Npix from the first row group.
    """
    if metadata.num_row_groups <= 0 or metadata.num_columns <= 0:
        raise ValueError("metadata is for empty table")
    order = -1
    pixel = -1
    first_row_group = metadata.row_group(0)
    for i in range(0, first_row_group.num_columns):
        column = first_row_group.column(i)
        if column.path_in_schema == norder_column:
            if column.statistics.min != column.statistics.max:
                raise ValueError(
                    f"{norder_column} stat min != max ({column.statistics.min} != {column.statistics.max})"
                )
            order = column.statistics.min
        elif column.path_in_schema == npix_column:
            if column.statistics.min != column.statistics.max:
                raise ValueError(
                    f"{npix_column} stat min != max ({column.statistics.min} != {column.statistics.max})"
                )
            pixel = column.statistics.min

    if order == -1 or pixel == -1:
        raise ValueError(f"Metadata missing Norder ({norder_column}) or Npix ({npix_column}) column")
    return HealpixPixel(order, pixel)


def write_parquet_metadata(
    catalog_path: str,
    order_by_healpix=True,
    output_path: str = None,
    *,
    input_file_system=None,
    input_storage_options: dict = None,
    output_file_system=None,
    output_storage_options: dict = None,
    file_system=None,
    storage_options: dict = None,
):
    """Generate parquet metadata, using the already-partitioned parquet files
    for this catalog.

    For more information on the general parquet metadata files, and why we write them, see
    https://arrow.apache.org/docs/python/parquet.html#writing-metadata-and-common-metadata-files

    Args:
        catalog_path (str): base path for the catalog
        order_by_healpix (bool): use False if the dataset is not to be reordered by
            breadth-first healpix pixel (e.g. secondary indexes)
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified
        input_file_system: fsspec or pyarrow filesystem for input parquet files, default None
        input_storage_options: dictionary that contains abstract filesystem credentials
            for the INPUT file system
        output_file_system: fsspec or pyarrow filesystem for output, default None
        output_storage_options: dictionary that contains abstract filesystem credentials
            for the OUTPUT file system
        file_system: fsspec or pyarrow filesystem for input AND output files, default None
        input_storage_options: dictionary that contains abstract filesystem credentials
            for both INPUT AND OUTPUT file system

    Returns:
        sum of the number of rows in the dataset.
    """
    # pylint: disable=too-many-locals
    ignore_prefixes = [
        "intermediate",
        "_common_metadata",
        "_metadata",
    ]

    input_file_system = input_file_system or file_system
    input_storage_options = input_storage_options or storage_options
    output_file_system = output_file_system or file_system
    output_storage_options = output_storage_options or storage_options

    (dataset_path, dataset) = file_io.read_parquet_dataset(
        catalog_path,
        file_system=input_file_system,
        storage_options=input_storage_options,
        ignore_prefixes=ignore_prefixes,
        exclude_invalid_files=True,
    )
    metadata_collector = []
    # Collect the healpix pixels so we can sort before writing.
    healpix_pixels = []
    total_rows = 0

    for hips_file in dataset.files:
        hips_file_pointer = file_io.get_file_pointer_from_path(hips_file, include_protocol=catalog_path)
        single_metadata = file_io.read_parquet_metadata(
            hips_file_pointer, file_system=input_file_system, storage_options=input_storage_options
        )

        # Users must set the file path of each chunk before combining the metadata.
        relative_path = hips_file[len(dataset_path) :]
        single_metadata.set_file_path(relative_path)

        if order_by_healpix:
            healpix_pixel = paths.get_healpix_from_path(relative_path)
            if healpix_pixel == INVALID_PIXEL:
                healpix_pixel = get_healpix_pixel_from_metadata(single_metadata)

            healpix_pixels.append(healpix_pixel)
        metadata_collector.append(single_metadata)
        total_rows += single_metadata.num_rows

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
        file_system=output_file_system,
        storage_options=output_storage_options,
    )
    file_io.write_parquet_metadata(
        dataset.schema,
        common_metadata_file_pointer,
        file_system=output_file_system,
        storage_options=output_storage_options,
    )
    return total_rows


def write_parquet_metadata_for_batches(
    batches: List[List[pa.RecordBatch]],
    output_path: str = None,
    *,
    file_system=None,
    storage_options: dict = None,
):
    """Write parquet metadata files for some pyarrow table batches.
    This writes the batches to a temporary parquet dataset using local storage, and
    generates the metadata for the partitioned catalog parquet files.

    Args:
        batches (List[List[pa.RecordBatch]]): create one row group per RecordBatch, grouped
            into tables by the inner list.
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials

    Returns:
        sum of the number of rows in the dataset.
    """

    with tempfile.TemporaryDirectory() as temp_pq_file:
        for batch_list in batches:
            temp_info_table = pa.Table.from_batches(batch_list)
            pq.write_to_dataset(temp_info_table, temp_pq_file)
        return write_parquet_metadata(
            temp_pq_file,
            output_file_system=file_system,
            output_storage_options=storage_options,
            output_path=output_path,
        )


def read_row_group_fragments(metadata_file: str, *, file_system=None, storage_options: dict = None):
    """Generator for metadata fragment row groups in a parquet metadata file.

    Args:
        metadata_file (str): path to `_metadata` file.
        file_system: fsspec or pyarrow filesystem, default None
        storage_options: dictionary that contains abstract filesystem credentials
    """
    if not file_io.is_regular_file(metadata_file, file_system=file_system, storage_options=storage_options):
        metadata_file = paths.get_parquet_metadata_pointer(metadata_file)
    file_system, file_pointer = get_fs(
        file_pointer=metadata_file, file_system=file_system, storage_options=storage_options
    )
    file_pointer = strip_leading_slash_for_pyarrow(file_pointer, file_system.protocol)
    dataset = pds.parquet_dataset(file_pointer, filesystem=file_system)

    for frag in dataset.get_fragments():
        yield from frag.row_groups
