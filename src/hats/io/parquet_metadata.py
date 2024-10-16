"""Utility functions for handling parquet metadata files"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List

import numpy as np
import pyarrow as pa
import pyarrow.dataset as pds
import pyarrow.parquet as pq
from upath import UPath

from hats.io import file_io, paths
from hats.io.file_io.file_pointer import get_upath
from hats.pixel_math.healpix_pixel import INVALID_PIXEL, HealpixPixel
from hats.pixel_math.healpix_pixel_function import get_pixel_argsort


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
    catalog_path: str | Path | UPath,
    order_by_healpix=True,
    output_path: str | Path | UPath | None = None,
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

    Returns:
        sum of the number of rows in the dataset.
    """
    ignore_prefixes = [
        "intermediate",
        "_common_metadata",
        "_metadata",
    ]

    catalog_path = get_upath(catalog_path)
    dataset_subdir = catalog_path / "dataset"
    (dataset_path, dataset) = file_io.read_parquet_dataset(
        dataset_subdir,
        ignore_prefixes=ignore_prefixes,
        exclude_invalid_files=True,
    )
    metadata_collector = []
    # Collect the healpix pixels so we can sort before writing.
    healpix_pixels = []
    total_rows = 0

    for single_file in dataset.files:
        relative_path = single_file[len(dataset_path) + 1 :]
        single_metadata = file_io.read_parquet_metadata(dataset_subdir / relative_path)

        # Users must set the file path of each chunk before combining the metadata.
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
    catalog_base_dir = get_upath(output_path)
    file_io.make_directory(catalog_base_dir / "dataset", exist_ok=True)
    metadata_file_pointer = paths.get_parquet_metadata_pointer(catalog_base_dir)
    common_metadata_file_pointer = paths.get_common_metadata_pointer(catalog_base_dir)

    file_io.write_parquet_metadata(
        dataset.schema,
        metadata_file_pointer,
        metadata_collector=metadata_collector,
        write_statistics=True,
    )
    file_io.write_parquet_metadata(dataset.schema, common_metadata_file_pointer)
    return total_rows


def write_parquet_metadata_for_batches(batches: List[List[pa.RecordBatch]], output_path: str = None):
    """Write parquet metadata files for some pyarrow table batches.
    This writes the batches to a temporary parquet dataset using local storage, and
    generates the metadata for the partitioned catalog parquet files.

    Args:
        batches (List[List[pa.RecordBatch]]): create one row group per RecordBatch, grouped
            into tables by the inner list.
        output_path (str): base path for writing out metadata files
            defaults to `catalog_path` if unspecified

    Returns:
        sum of the number of rows in the dataset.
    """

    with tempfile.TemporaryDirectory() as temp_pq_file:
        temp_dataset_dir = get_upath(temp_pq_file) / "dataset"
        temp_dataset_dir.mkdir()
        for batch_list in batches:
            temp_info_table = pa.Table.from_batches(batch_list)
            pq.write_to_dataset(temp_info_table, temp_dataset_dir)
        return write_parquet_metadata(temp_pq_file, output_path=output_path)


def read_row_group_fragments(metadata_file: str):
    """Generator for metadata fragment row groups in a parquet metadata file.

    Args:
        metadata_file (str): path to `_metadata` file.
    """
    metadata_file = get_upath(metadata_file)
    if not file_io.is_regular_file(metadata_file):
        metadata_file = paths.get_parquet_metadata_pointer(metadata_file)

    dataset = pds.parquet_dataset(metadata_file, filesystem=metadata_file.fs)

    for frag in dataset.get_fragments():
        yield from frag.row_groups
